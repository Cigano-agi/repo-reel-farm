import asyncio
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import farm


class FarmTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.episode = Path(self.tmp.name)
        (self.episode / "episode.json").write_text(
            json.dumps({"slug": "test", "title": "Teste", "language": "pt-BR", "sourceRepo": "https://example.org/repo", "ctaText": "Guilda", "render": {"width": 1080, "height": 1920}}), encoding="utf-8"
        )
        (self.episode / "BRIEF.md").write_text("Pauta factual", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_parallel_cache_and_research_invalidation(self):
        async def scenario():
            first = await farm.run(self.episode, {}, 3, True, False)
            second = await farm.run(self.episode, {}, 3, True, False)
            self.assertTrue(all(v.get("cached") for v in second["results"].values()))
            self.assertLess(first["elapsedSeconds"], 0.4)
            (self.episode / "BRIEF.md").write_text("Pauta factual revisada", encoding="utf-8")
            third = await farm.run(self.episode, {}, 3, True, False)
            self.assertFalse(third["results"]["research_social"].get("cached", False))
            self.assertFalse(third["results"]["copy_editorial"].get("cached", False))
        asyncio.run(scenario())

    def test_gate_blocks_producer(self):
        original = farm.invoke

        async def reject(role, episode_dir, provider, upstream, mock):
            if role == "facts_product":
                return {"status": "fail", "summary": "Claim sem prova", "evidence": [], "outputs": [], "issues": ["claim"]}
            return await original(role, episode_dir, provider, upstream, mock)

        with patch.object(farm, "invoke", side_effect=reject):
            result = asyncio.run(farm.run(self.episode, {}, 3, True, True))
        self.assertEqual(result["results"]["copy_editorial"]["status"], "blocked")
        self.assertEqual(result["results"]["producer"]["status"], "blocked")

    def test_producer_requires_real_delivery_files(self):
        result = {"status": "pass", "summary": "pronto", "evidence": ["source"], "outputs": [], "issues": []}
        with self.assertRaisesRegex(ValueError, "faltam 2 MP4"):
            farm.validate_outputs("producer", self.episode, result, False)
        files = ["delivery/music.mp4", "delivery/clean.mp4", "delivery/cover.png", "delivery/contact.jpg", "index.html"]
        samples = {".mp4": b"fixture", ".png": b"\x89PNG\r\n\x1a\nfixture", ".jpg": b"\xff\xd8\xfffixture", ".html": b"<html>fixture</html>"}
        for name in files:
            path = self.episode / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(samples[path.suffix])
        result["outputs"] = files
        with patch.object(farm, "probe_mp4", return_value={"fps": 60, "duration": 1}):
            self.assertEqual(len(farm.validate_outputs("producer", self.episode, result, False)), 5)
        result["outputs"] = ["delivery/music.mp4", "delivery/../delivery/music.mp4", *files[2:]]
        with self.assertRaisesRegex(ValueError, "Output repetido"):
            farm.validate_outputs("producer", self.episode, result, False)
        result["outputs"] = files
        (self.episode / "delivery/clean.mp4").unlink()
        with self.assertRaisesRegex(ValueError, "Output ausente"):
            farm.validate_outputs("producer", self.episode, result, False)

    def test_voice_brief_part_of_cache_context(self):
        episode = farm.read_json(self.episode / "episode.json")
        light = farm.role_context("voice_casting", episode, "voz aguda", {})
        deep = farm.role_context("voice_casting", episode, "voz grave", {})
        self.assertNotEqual(farm.digest(light), farm.digest(deep))


if __name__ == "__main__":
    unittest.main()
