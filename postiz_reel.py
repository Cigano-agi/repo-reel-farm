"""Stage a reviewed Repo Reel for Postiz; remote action is draft-only.

The CLI never schedules or publishes. Media and receipts stay under ignored work/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def inside(root: Path, path: Path) -> Path:
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root.resolve(strict=True)):
        raise ValueError(f"Arquivo fora do episódio: {path}")
    return resolved


def probe_video(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode:
        raise ValueError(f"MP4 inválido: {path.name}")
    info = json.loads(result.stdout)
    stream = (info.get("streams") or [{}])[0]
    fps = stream.get("r_frame_rate", "0/1")
    numerator, denominator = map(int, fps.split("/"))
    duration = float(info.get("format", {}).get("duration", 0))
    if (stream.get("width"), stream.get("height")) != (1080, 1920) or denominator == 0 or numerator / denominator < 29.9 or duration < 1:
        raise ValueError("Reel precisa ser 1080×1920, ≥30 fps e ≥1 s")
    return {"durationSeconds": duration, "fps": numerator / denominator}


def prepare(episode_dir: Path, caption_path: Path, profile: str = "cigano.agi") -> Path:
    episode_dir = episode_dir.resolve(strict=True)
    episode = read_json(episode_dir / "episode.json")
    slug = episode["slug"]
    video = inside(episode_dir, episode_dir / "delivery" / f"{slug}-com-musica.mp4")
    qa = inside(episode_dir, episode_dir / "qa" / "QA.md")
    caption = inside(episode_dir, episode_dir / caption_path)
    text = caption.read_text(encoding="utf-8-sig").strip()
    if not 0 < len(text) <= 2200:
        raise ValueError("Legenda precisa ter 1–2200 caracteres")
    probe = probe_video(video)
    episode_hash = sha256(episode_dir / "episode.json")
    run_path = episode_dir / "work" / "run.json"
    run_hash = sha256(run_path) if run_path.is_file() else None
    revision = hashlib.sha256((episode_hash + sha256(video) + sha256(caption) + sha256(qa) + str(run_hash) + profile).encode()).hexdigest()[:12]
    target = episode_dir / "work" / "postiz" / f"reel-{revision}.manifest.json"
    if target.exists():
        inspect(target)
        return target
    save_json(target, {
        "schema": 1, "episode": slug, "profile": profile, "caption": text,
        "episodeSha256": episode_hash, "runSha256": run_hash,
        "video": str(video.relative_to(episode_dir)), "videoSha256": sha256(video),
        "captionFile": str(caption.relative_to(episode_dir)), "captionSha256": sha256(caption),
        "qaFile": str(qa.relative_to(episode_dir)), "qaSha256": sha256(qa),
        "probe": probe, "status": "local-prepared", "remotePostId": None,
    })
    return target


def inspect(manifest_path: Path) -> dict:
    manifest_path = manifest_path.resolve(strict=True)
    episode_dir = manifest_path.parents[2]
    manifest = read_json(manifest_path)
    if manifest_path.parent != episode_dir / "work" / "postiz" or not manifest_path.name.startswith("reel-") or not manifest_path.name.endswith(".manifest.json"):
        raise ValueError("Manifesto fora do local esperado")
    video = inside(episode_dir, episode_dir / manifest["video"])
    caption = inside(episode_dir, episode_dir / manifest["captionFile"])
    qa = inside(episode_dir, episode_dir / manifest["qaFile"])
    for path, key in ((video, "videoSha256"), (caption, "captionSha256"), (qa, "qaSha256")):
        if sha256(path) != manifest[key]:
            raise ValueError(f"Arquivo mudou após preparo: {path.name}")
    if caption.read_text(encoding="utf-8-sig").strip() != manifest["caption"]:
        raise ValueError("Legenda divergente")
    probe_video(video)
    episode = read_json(episode_dir / "episode.json")
    if sha256(episode_dir / "episode.json") != manifest["episodeSha256"]:
        raise ValueError("Manifesto do episódio mudou após preparo")
    rights = episode.get("rights", {})
    approval = episode.get("approval", {})
    run_path = episode_dir / "work" / "run.json"
    run_unchanged = run_path.is_file() and sha256(run_path) == manifest.get("runSha256")
    run_ready = run_unchanged and read_json(run_path).get("publicationReady") is True
    ready = (run_ready and rights.get("thirdPartyVideo") in {"cleared", "none-used"}
             and rights.get("pageScreenshots") in {"cleared", "none-used"}
             and rights.get("voice") == "cleared" and approval.get("humanAudio") is True
             and approval.get("editorial") is True)
    return {"episode": manifest["episode"], "localPrepared": True, "remoteEligible": ready,
            "video": str(video), "profile": manifest["profile"], "status": manifest["status"]}


def cli(*args: str) -> object:
    script = os.environ.get("POSTIZ_CLI_JS")
    if not script:
        script = str(Path(os.environ.get("LOCALAPPDATA", "")) / "CiganoTools/postiz/node_modules/postiz/dist/index.js")
    if not Path(script).is_file():
        raise RuntimeError("Postiz CLI ausente; configure POSTIZ_CLI_JS")
    result = subprocess.run(["node", script, *args], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=300, check=False)
    if result.returncode:
        diagnostic = (result.stdout + result.stderr).lower()
        if "no authentication found" in diagnostic or "not authenticated" in diagnostic or "não autenticado" in diagnostic:
            raise RuntimeError("Postiz não autenticado; conecte a instância antes de consultar canais")
        raise RuntimeError("Postiz falhou; confira autenticação, instância e calendário antes de repetir")
    lines = result.stdout.splitlines()
    for index, line in enumerate(lines):
        if line.lstrip().startswith(("{", "[")):
            try:
                return json.loads("\n".join(lines[index:]))
            except json.JSONDecodeError:
                continue
    raise RuntimeError("Postiz não retornou JSON; confira estado remoto antes de repetir")


def draft(manifest_path: Path, integration: str, run=cli) -> dict:
    state = inspect(manifest_path)
    if not state["remoteEligible"]:
        raise ValueError("Direitos, QA ou aceite humano pendentes; upload remoto bloqueado")
    manifest_path = manifest_path.resolve(strict=True)
    receipt = manifest_path.with_suffix(".receipt.json")
    lock = manifest_path.with_suffix(".lock")
    if receipt.exists() or lock.exists():
        raise FileExistsError("Tentativa anterior existe; reconcilie no Postiz antes de repetir")
    channels = run("integrations:list")
    if not isinstance(channels, list):
        raise ValueError("Lista de canais inválida")
    channel = next((item for item in channels if item.get("id") == integration), None)
    if not channel or channel.get("disabled") or channel.get("identifier") not in {"instagram", "instagram-standalone"}:
        raise ValueError("Integração Instagram indisponível")
    if str(channel.get("profile", "")).lstrip("@").lower() != state["profile"].lstrip("@").lower():
        raise ValueError("Perfil conectado não corresponde ao manifesto")
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    record = {"status": "uploading", "manifestSha256": sha256(manifest_path), "integration": integration}
    try:
        save_json(receipt, record)
        manifest = read_json(manifest_path)
        uploaded = run("upload", state["video"])
        if not isinstance(uploaded, dict) or not uploaded.get("id") or not str(uploaded.get("path", "")).startswith("https://"):
            raise ValueError("Upload não retornou ID e URL HTTPS")
        if not inspect(manifest_path)["remoteEligible"]:
            raise ValueError("Aceite revogado ou pendente após upload; rascunho não criado")
        if sha256(manifest_path) != record["manifestSha256"]:
            raise ValueError("Manifesto mudou durante upload")
        payload = {"type": "draft", "date": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "shortLink": False, "tags": [], "posts": [{"integration": {"id": integration},
                   "value": [{"content": manifest["caption"], "image": [{"id": uploaded["id"], "path": uploaded["path"]}]}],
                   "settings": {"__type": channel["identifier"], "post_type": "post"}}]}
        payload_path = manifest_path.with_suffix(".payload.json")
        save_json(payload_path, payload)
        if not inspect(manifest_path)["remoteEligible"]:
            raise ValueError("Aceite revogado ou pendente antes de criar rascunho")
        record["status"] = "creating_remote_draft"
        record["upload"] = {"id": uploaded["id"], "path": uploaded["path"]}
        save_json(receipt, record)
        result = run("posts:create", "--json", str(payload_path))
        if not isinstance(result, list) or not result or not result[0].get("postId"):
            raise ValueError("Postiz não confirmou postId")
        record["status"] = "draft_created"
        record["postId"] = result[0]["postId"]
        save_json(receipt, record)
        return record
    except Exception:
        record["status"] = "needs_reconciliation"
        save_json(receipt, record)
        raise
    finally:
        lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("episode", type=Path)
    prep.add_argument("--caption", type=Path, required=True, help="Arquivo dentro do episódio")
    check = sub.add_parser("inspect")
    check.add_argument("manifest", type=Path)
    send = sub.add_parser("draft")
    send.add_argument("manifest", type=Path)
    send.add_argument("--integration", required=True)
    sub.add_parser("channels")
    args = parser.parse_args()
    if args.command == "prepare":
        result = {"manifest": str(prepare(args.episode, args.caption))}
    elif args.command == "inspect":
        result = inspect(args.manifest)
    elif args.command == "channels":
        result = cli("integrations:list")
    else:
        result = draft(args.manifest, args.integration)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, FileNotFoundError, FileExistsError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        raise SystemExit(1)
