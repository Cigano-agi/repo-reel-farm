import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import postiz_reel


class PostizReelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "episode"
        for folder in ("delivery", "qa", "work/postiz"):
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        (self.root / "episode.json").write_text(json.dumps({
            "slug": "test", "rights": {"thirdPartyVideo": "none-used", "pageScreenshots": "private-editorial-review", "voice": "pending"},
            "approval": {"humanAudio": False, "editorial": False},
        }), encoding="utf-8")
        (self.root / "delivery/test-com-musica.mp4").write_bytes(b"fake-video-for-manifest-test")
        (self.root / "qa/QA.md").write_text("QA factual e visual", encoding="utf-8")
        self.caption = self.root / "work/postiz/LEGENDA.txt"
        self.caption.write_text("Teste com fonte e limite.", encoding="utf-8")
        self.probe = patch.object(postiz_reel, "probe_video", return_value={"durationSeconds": 30, "fps": 60})
        self.probe.start()

    def tearDown(self):
        self.probe.stop()
        self.temp.cleanup()

    def test_prepare_detects_media_change_and_blocks_remote_when_pending(self):
        manifest = postiz_reel.prepare(self.root, Path("work/postiz/LEGENDA.txt"))
        self.assertFalse(postiz_reel.inspect(manifest)["remoteEligible"])
        with self.assertRaisesRegex(ValueError, "pendentes"):
            postiz_reel.draft(manifest, "instagram-id", run=lambda *_: self.fail("remote call"))
        (self.root / "delivery/test-com-musica.mp4").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "mudou"):
            postiz_reel.inspect(manifest)

    def test_approved_revision_creates_one_draft_and_refuses_duplicate(self):
        episode_path = self.root / "episode.json"
        episode = json.loads(episode_path.read_text(encoding="utf-8"))
        episode["rights"].update(pageScreenshots="cleared", voice="cleared")
        episode["approval"] = {"humanAudio": True, "editorial": True}
        episode_path.write_text(json.dumps(episode), encoding="utf-8")
        (self.root / "work/run.json").write_text(json.dumps({"publicationReady": True}), encoding="utf-8")
        manifest = postiz_reel.prepare(self.root, Path("work/postiz/LEGENDA.txt"))
        calls = []

        def fake(*args):
            calls.append(args[0])
            if args[0] == "integrations:list":
                return [{"id": "instagram-id", "identifier": "instagram", "profile": "cigano.agi"}]
            if args[0] == "upload":
                return {"id": "media-id", "path": "https://postiz.example/media.mp4"}
            payload = json.loads(Path(args[-1]).read_text(encoding="utf-8"))
            self.assertEqual(payload["type"], "draft")
            self.assertEqual(payload["posts"][0]["settings"]["post_type"], "post")
            self.assertEqual(payload["posts"][0]["value"][0]["image"][0]["id"], "media-id")
            return [{"postId": "draft-id"}]

        receipt = postiz_reel.draft(manifest, "instagram-id", run=fake)
        self.assertEqual(receipt["status"], "draft_created")
        self.assertEqual(calls, ["integrations:list", "upload", "posts:create"])
        with self.assertRaises(FileExistsError):
            postiz_reel.draft(manifest, "instagram-id", run=fake)
        self.assertEqual(len(calls), 3)

    def test_revoked_during_upload_never_creates_remote_draft(self):
        episode_path = self.root / "episode.json"
        episode = json.loads(episode_path.read_text(encoding="utf-8"))
        episode["rights"].update(pageScreenshots="cleared", voice="cleared")
        episode["approval"] = {"humanAudio": True, "editorial": True}
        episode_path.write_text(json.dumps(episode), encoding="utf-8")
        run_path = self.root / "work/run.json"
        run_path.write_text(json.dumps({"publicationReady": True}), encoding="utf-8")
        manifest = postiz_reel.prepare(self.root, Path("work/postiz/LEGENDA.txt"))
        calls = []

        def fake(*args):
            calls.append(args[0])
            if args[0] == "integrations:list":
                return [{"id": "instagram-id", "identifier": "instagram", "profile": "cigano.agi"}]
            if args[0] == "upload":
                run_path.write_text(json.dumps({"publicationReady": False}), encoding="utf-8")
                return {"id": "media-id", "path": "https://postiz.example/media.mp4"}
            self.fail("posts:create após revogar gate")

        with self.assertRaisesRegex(ValueError, "revogad|pendente|alterad"):
            postiz_reel.draft(manifest, "instagram-id", run=fake)
        self.assertEqual(calls, ["integrations:list", "upload"])
        self.assertEqual(json.loads(manifest.with_suffix(".receipt.json").read_text(encoding="utf-8"))["status"], "needs_reconciliation")

    def test_cli_decodes_utf8_even_when_windows_codepage_differs(self):
        with patch.object(postiz_reel.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="Não autenticado")) as process:
            with self.assertRaisesRegex(RuntimeError, "Postiz não autenticado"):
                postiz_reel.cli("integrations:list")
        self.assertEqual(process.call_args.kwargs["encoding"], "utf-8")
        self.assertEqual(process.call_args.kwargs["errors"], "replace")


if __name__ == "__main__":
    unittest.main()
