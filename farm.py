"""Small, provider-neutral agent farm for evidence-led short videos.

Python 3.11+; no third-party Python dependencies. Run ``python farm.py --help``.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
ROLES = {
    "research_social": (),
    "facts_product": (),
    "voice_casting": (),
    "copy_editorial": ("research_social", "facts_product"),
    "motion_direction": ("copy_editorial",),
    "producer": ("motion_direction", "voice_casting"),
    "qa_visual": ("producer",),
    "red_team": ("producer",),
}
GATE_A = {"research_social", "facts_product", "voice_casting"}
GATE_B = {"copy_editorial", "motion_direction"}
PROMPT_VERSION = 3


def digest(data: object) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_episode(episode: dict) -> None:
    required = ("slug", "title", "language", "sourceRepo", "ctaText", "render")
    missing = [key for key in required if not episode.get(key)]
    if missing:
        raise ValueError(f"episode.json sem: {', '.join(missing)}")
    if episode["language"] != "pt-BR":
        raise ValueError("Este fluxo requer language: pt-BR")
    if not episode["sourceRepo"].startswith("https://"):
        raise ValueError("sourceRepo precisa ser uma URL HTTPS")
    if episode["render"].get("width") != 1080 or episode["render"].get("height") != 1920:
        raise ValueError("Render esperado: 1080 x 1920")


def role_context(role: str, episode: dict, brief: str, upstream: dict) -> dict:
    fields = {
        "research_social": ("slug", "title", "sourceRepo", "sourcePost"),
        "facts_product": ("slug", "title", "sourceRepo", "claims"),
        "voice_casting": ("slug", "title", "language", "knownTools", "pronunciationMap"),
        "copy_editorial": tuple(episode.keys()),
        "motion_direction": ("slug", "title", "render", "ctaText"),
        "producer": tuple(episode.keys()),
        "qa_visual": ("slug", "render", "rights", "ctaText"),
        "red_team": ("slug", "title", "sourceRepo", "sourcePost", "claims", "ctaText", "rights"),
    }[role]
    return {
        "episode": {key: episode[key] for key in fields if key in episode},
        "brief": brief if role in {"research_social", "facts_product", "voice_casting", "copy_editorial"} else None,
        "upstream": upstream,
    }


def prompt_for(role: str, episode_dir: Path, upstream: dict) -> str:
    episode = read_json(episode_dir / "episode.json")
    context = role_context(role, episode, (episode_dir / "BRIEF.md").read_text(encoding="utf-8"), upstream)
    specific = {
        "research_social": "Valide post, autor, data, vídeo/artefato e trechos visuais. Cite URLs e limites. Não invente prova.",
        "facts_product": "Valide README, licença, instalação, limites e claims. Entregue matriz claim→prova→limite.",
        "voice_casting": "Teste vozes brasileiras com nomes técnicos; registre comparação e hash do take escolhido. Não exponha chaves.",
        "copy_editorial": "Escreva mistério→mecanismo→prova humana→aplicação→Guilda. Gancho até 3s; CTA exato do manifesto. Inclua roteiro e palavras.",
        "motion_direction": "Crie storyboard temporal de browser dirigido, prova real legível, aplicação e WhatsApp ilustrativo. Indique SFX e safe zone.",
        "producer": "Único editor da composição. Produza e liste em outputs duas MP4 (música/limpo), capa PNG, contato JPG e composição HTML existentes dentro do episódio. Preserve vídeos existentes. Use Hypit por .svrun apenas para um protótipo que ele suporte; registre build ID e limites; render final pelo motor escolhido.",
        "qa_visual": "Revise MP4 final sem áudio, com áudio e em escala de celular. Cheque duração, 1080x1920/60fps, LUFS/pico, leitura, prova, direitos e CTA. Grave QA em Markdown e liste o arquivo em outputs. Não edite composição.",
        "red_team": "Tente reprovar hype sem prova, aplicação vaga, CTA abrupto, slop, pronúncia e direitos. Grave parecer Markdown e liste em outputs. Não edite composição.",
    }[role]
    return (
        "Você é o especialista " + role + " da farm Repo Reel. Responda em português brasileiro.\n"
        + specific + "\n"
        + f"Trabalhe somente em seu diretório de trabalho. Pasta do episódio: {episode_dir}. Caminhos em outputs são relativos à pasta do episódio. Não publique nem envie a terceiros.\n"
        + "Ao final responda APENAS JSON válido com as chaves: status ('pass' ou 'fail'), summary, evidence (lista de URLs ou caminhos), outputs (lista de caminhos), issues (lista)."
        + " QA e red_team podem usar fail para reprovar. Gate A/B exige pass e evidência.\n"
        + "CONTEXTO:\n" + json.dumps(context, ensure_ascii=False, indent=2)
    )


def parse_agent_result(raw: str, role: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    value = json.loads(raw)
    if value.get("status") not in {"pass", "fail"}:
        raise ValueError(f"{role}: status deve ser pass/fail")
    for key in ("summary", "evidence", "outputs", "issues"):
        if key not in value:
            raise ValueError(f"{role}: falta {key}")
    if not isinstance(value["summary"], str) or any(not isinstance(value[key], list) for key in ("evidence", "outputs", "issues")):
        raise ValueError(f"{role}: tipos inválidos no resultado")
    if any(not isinstance(item, str) for key in ("evidence", "outputs", "issues") for item in value[key]):
        raise ValueError(f"{role}: listas devem conter texto")
    if role in GATE_A | GATE_B and value["status"] == "pass" and not value["evidence"]:
        raise ValueError(f"{role}: gate exige evidência")
    return value


def output_fingerprints(episode_dir: Path, result: dict) -> dict[str, str]:
    fingerprints = {}
    seen = set()
    for item in result.get("outputs", []):
        path = (episode_dir / item).resolve()
        if not path.is_relative_to(episode_dir.resolve()) or not path.is_file():
            raise ValueError(f"Output ausente ou fora do episódio: {item}")
        if path in seen:
            raise ValueError(f"Output repetido por alias: {item}")
        seen.add(path)
        sha = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                sha.update(chunk)
        fingerprints[item] = sha.hexdigest()
    return fingerprints


def probe_mp4(path: Path) -> dict:
    tool = shutil.which("ffprobe")
    if not tool:
        raise ValueError("ffprobe é necessário para validar os MP4")
    result = subprocess.run(
        [tool, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode:
        raise ValueError(f"MP4 inválido: {path.name}: {result.stderr[-300:]}")
    info = json.loads(result.stdout)
    streams = info.get("streams", [])
    if not streams:
        raise ValueError(f"MP4 sem vídeo: {path.name}")
    stream = streams[0]
    numerator, denominator = map(int, stream.get("r_frame_rate", "0/1").split("/"))
    fps = numerator / denominator if denominator else 0
    duration = float(info.get("format", {}).get("duration", 0))
    if (stream.get("width"), stream.get("height")) != (1080, 1920) or fps < 59.9 or duration < 1:
        raise ValueError(f"MP4 fora da especificação 1080×1920/60 fps: {path.name}")
    return {"fps": fps, "duration": duration}


def validate_outputs(role: str, episode_dir: Path, result: dict, mock: bool) -> dict[str, str]:
    if mock or result["status"] != "pass":
        return {}
    fingerprints = output_fingerprints(episode_dir, result)
    suffixes = [Path(item).suffix.lower() for item in fingerprints]
    if role == "producer" and not (suffixes.count(".mp4") >= 2 and all(s in suffixes for s in (".png", ".jpg", ".html"))):
        raise ValueError("producer: faltam 2 MP4, capa PNG, contato JPG ou composição HTML")
    if role == "producer":
        for item in fingerprints:
            path = (episode_dir / item).resolve()
            suffix = path.suffix.lower()
            if suffix == ".mp4":
                probe_mp4(path)
            elif suffix == ".png" and not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError(f"PNG inválido: {path.name}")
            elif suffix == ".jpg" and not path.read_bytes().startswith(b"\xff\xd8\xff"):
                raise ValueError(f"JPG inválido: {path.name}")
            elif suffix == ".html" and b"<html" not in path.read_bytes()[:4096].lower():
                raise ValueError(f"HTML inválido: {path.name}")
    if role in {"qa_visual", "red_team"} and ".md" not in suffixes:
        raise ValueError(f"{role}: falta parecer Markdown")
    return fingerprints


async def invoke(role: str, episode_dir: Path, provider: dict, upstream: dict, mock: bool) -> dict:
    workspace = episode_dir if role == "producer" else episode_dir / "work" / "roles" / role
    workspace.mkdir(parents=True, exist_ok=True)
    result_path = workspace / "result.json" if role != "producer" else workspace / "work" / "producer.agent.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    prompt = prompt_for(role, episode_dir, upstream)
    if mock:
        await asyncio.sleep(0.05)
        result = {"status": "pass", "summary": f"Mock {role}; não é prova editorial nem render", "evidence": ["mock://fixture"], "outputs": [], "issues": []}
        write_json(result_path, result)
        return result
    command = provider.get("command")
    if not isinstance(command, list) or not command:
        raise ValueError("Provider precisa de command como lista de argumentos")
    values = {"workspace": str(workspace), "output": str(result_path), "prompt": prompt}
    argv = [part.format_map(values) for part in command]
    result_path.unlink(missing_ok=True)
    started = time.monotonic()
    process = await asyncio.create_subprocess_exec(*argv, cwd=workspace, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=provider.get("timeoutSeconds", 1800))
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise RuntimeError(f"{role}: timeout")
    if process.returncode:
        raise RuntimeError(f"{role}: CLI saiu {process.returncode}: {stderr.decode(errors='replace')[-1200:]}")
    raw = stdout.decode(errors="replace") if provider.get("stdoutIsResult") else result_path.read_text(encoding="utf-8")
    result = parse_agent_result(raw, role)
    result["durationSeconds"] = round(time.monotonic() - started, 2)
    write_json(result_path, result)
    return result


async def run(episode_dir: Path, provider: dict, concurrency: int, mock: bool, force: bool, shared_semaphore: asyncio.Semaphore | None = None) -> dict:
    episode = read_json(episode_dir / "episode.json")
    validate_episode(episode)
    if not (episode_dir / "BRIEF.md").exists():
        raise ValueError("Falta BRIEF.md")
    cache_dir = episode_dir / ".farm-cache"
    cache_dir.mkdir(exist_ok=True)
    semaphore = shared_semaphore or asyncio.Semaphore(concurrency)
    tasks: dict[str, asyncio.Task] = {}
    results: dict[str, dict] = {}
    started = time.monotonic()

    async def one(role: str) -> dict:
        upstream = {dep: {k: v for k, v in (await tasks[dep]).items() if k != "cached"} for dep in ROLES[role]}
        if any(v["status"] != "pass" for v in upstream.values()):
            return {"status": "blocked", "summary": "Dependência reprovada", "evidence": [], "outputs": [], "issues": []}
        relevant = {
            "role": role,
            "context": role_context(role, episode, (episode_dir / "BRIEF.md").read_text(encoding="utf-8"), upstream),
            "promptVersion": PROMPT_VERSION,
            "provider": provider.get("command", []) if not mock else "mock",
        }
        key = digest(relevant)
        cache_path = cache_dir / f"{role}.json"
        if not force and cache_path.exists():
            cached = read_json(cache_path)
            fresh = role not in {"research_social", "facts_product"} or time.time() - cached.get("createdAt", 0) < 86400
            if fresh and cached.get("key") == key and cached.get("result", {}).get("status") == "pass":
                try:
                    current = output_fingerprints(episode_dir, cached["result"])
                    if current == cached.get("outputHashes", {}):
                        result = cached["result"] | {"cached": True}
                        results[role] = result
                        return result
                except ValueError:
                    pass
        async with semaphore:
            print(f"[{role}] início", flush=True)
            result = await invoke(role, episode_dir, provider, upstream, mock)
            hashes = validate_outputs(role, episode_dir, result, mock)
            print(f"[{role}] {result['status']}", flush=True)
        write_json(cache_path, {"key": key, "result": result, "outputHashes": hashes, "createdAt": time.time()})
        results[role] = result
        return result

    for role in ROLES:
        tasks[role] = asyncio.create_task(one(role))
    settled = await asyncio.gather(*tasks.values(), return_exceptions=True)
    for role, item in zip(ROLES, settled):
        if isinstance(item, BaseException):
            results[role] = {"status": "error", "summary": str(item), "evidence": [], "outputs": [], "issues": [str(item)]}
        elif role not in results:
            results[role] = item
    rights = episode.get("rights", {})
    approval = episode.get("approval", {})
    publication_ready = (
        not mock
        and all(row["status"] == "pass" for row in results.values())
        and rights.get("thirdPartyVideo") in {"cleared", "none-used"}
        and rights.get("pageScreenshots", "none-used") in {"cleared", "none-used"}
        and rights.get("voice") == "cleared"
        and approval.get("humanAudio") is True
        and approval.get("editorial") is True
    )
    final = {"episode": episode["slug"], "mock": mock, "elapsedSeconds": round(time.monotonic() - started, 2), "pipelinePassed": all(row["status"] == "pass" for row in results.values()), "publicationReady": publication_ready, "results": results}
    write_json(episode_dir / "work" / "run.json", final)
    return final


def main() -> int:
    parser = argparse.ArgumentParser(description="Farm de subagentes para vídeos Repo Reel")
    parser.add_argument("episode", nargs="?", help="Pasta do episódio, com episode.json e BRIEF.md")
    parser.add_argument("--batch-file", help="JSON com episodes[]; caminhos relativos ao arquivo")
    parser.add_argument("--provider", default="codex", help="Nome do provider em providers.json")
    parser.add_argument("--providers-file", default=str(ROOT / "providers.json"))
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--mock", action="store_true", help="Testa a DAG sem chamar LLM; resultados não têm valor editorial")
    parser.add_argument("--force", action="store_true", help="Ignora cache da farm")
    args = parser.parse_args()
    if args.concurrency < 1 or args.concurrency > 8:
        parser.error("--concurrency deve ficar entre 1 e 8")
    if bool(args.episode) == bool(args.batch_file):
        parser.error("Informe uma pasta de episódio OU --batch-file")
    if args.batch_file:
        batch_file = Path(args.batch_file).resolve()
        if not batch_file.is_file():
            parser.error("Arquivo batch inexistente")
        rows = read_json(batch_file).get("episodes")
        if not isinstance(rows, list) or not rows or any(not isinstance(row, str) for row in rows):
            parser.error("Batch precisa de episodes[] com caminhos")
        episode_dirs = [(batch_file.parent / row).resolve() for row in rows]
    else:
        episode_dirs = [Path(args.episode).resolve()]
    if any(not path.is_dir() for path in episode_dirs):
        parser.error("Pasta de episódio inexistente")
    if args.mock:
        provider = {}
    else:
        providers_path = Path(args.providers_file)
        if not providers_path.exists():
            parser.error(f"Crie {providers_path} a partir de providers.example.json")
        provider = read_json(providers_path).get(args.provider)
        if not provider:
            parser.error(f"Provider {args.provider} não encontrado")
        if not shutil.which(provider["command"][0]):
            parser.error(f"CLI indisponível: {provider['command'][0]}")
    async def execute() -> list[dict]:
        shared = asyncio.Semaphore(args.concurrency)
        return await asyncio.gather(*(run(path, provider, args.concurrency, args.mock, args.force, shared) for path in episode_dirs))
    finals = asyncio.run(execute())
    print(json.dumps([{"episode": final["episode"], "mock": final["mock"], "elapsedSeconds": final["elapsedSeconds"], "pipelinePassed": final["pipelinePassed"], "publicationReady": final["publicationReady"], "statuses": {k: v["status"] for k, v in final["results"].items()}} for final in finals], ensure_ascii=False, indent=2))
    return 0 if all(final["pipelinePassed"] for final in finals) else 1


if __name__ == "__main__":
    sys.exit(main())
