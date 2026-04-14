import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class CavemanModeTrackerTests(unittest.TestCase):
    """Tests for /caveman mode tracking via caveman-mode-tracker.js."""

    def run_tracker(self, prompt, home):
        env = os.environ.copy()
        env["HOME"] = str(home)
        payload = json.dumps({"prompt": prompt})
        result = subprocess.run(
            ["node", str(REPO_ROOT / "hooks" / "caveman-mode-tracker.js")],
            input=payload,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        return result

    def read_flag(self, home):
        flag = Path(home) / ".claude" / ".caveman-active"
        if flag.exists():
            return flag.read_text().strip()
        return None

    def test_caveman_default_writes_full(self):
        with tempfile.TemporaryDirectory(prefix="caveman-full-") as tmp:
            home = Path(tmp)
            (home / ".claude").mkdir(parents=True)
            self.run_tracker("/caveman", home)
            mode = self.read_flag(home)
            self.assertIn(mode, ("full", "lite", "ultra"),
                          f"Modo padrao esperado ser full/lite/ultra, recebeu: {mode}")

    def test_lite_writes_lite(self):
        with tempfile.TemporaryDirectory(prefix="caveman-lite-") as tmp:
            home = Path(tmp)
            (home / ".claude").mkdir(parents=True)
            self.run_tracker("/caveman lite", home)
            self.assertEqual(self.read_flag(home), "lite")

    def test_ultra_writes_ultra(self):
        with tempfile.TemporaryDirectory(prefix="caveman-ultra-") as tmp:
            home = Path(tmp)
            (home / ".claude").mkdir(parents=True)
            self.run_tracker("/caveman ultra", home)
            self.assertEqual(self.read_flag(home), "ultra")

    def test_stop_caveman_clears_flag(self):
        with tempfile.TemporaryDirectory(prefix="caveman-stop-") as tmp:
            home = Path(tmp)
            claude_dir = home / ".claude"
            claude_dir.mkdir(parents=True)
            flag = claude_dir / ".caveman-active"
            flag.write_text("full")
            self.run_tracker("stop caveman", home)
            self.assertIsNone(self.read_flag(home))

    def test_normal_mode_clears_flag(self):
        with tempfile.TemporaryDirectory(prefix="caveman-normal-") as tmp:
            home = Path(tmp)
            claude_dir = home / ".claude"
            claude_dir.mkdir(parents=True)
            flag = claude_dir / ".caveman-active"
            flag.write_text("ultra")
            self.run_tracker("normal mode", home)
            self.assertIsNone(self.read_flag(home))

    def test_commit_writes_commit(self):
        with tempfile.TemporaryDirectory(prefix="caveman-commit-") as tmp:
            home = Path(tmp)
            (home / ".claude").mkdir(parents=True)
            self.run_tracker("/caveman-commit", home)
            self.assertEqual(self.read_flag(home), "commit")

    def test_review_writes_review(self):
        with tempfile.TemporaryDirectory(prefix="caveman-review-") as tmp:
            home = Path(tmp)
            (home / ".claude").mkdir(parents=True)
            self.run_tracker("/caveman-review", home)
            self.assertEqual(self.read_flag(home), "review")


class CavemanStatuslineBashTests(unittest.TestCase):
    """Tests for caveman-statusline.sh with base modes."""

    def run_statusline(self, mode, home):
        flag = Path(home) / ".claude" / ".caveman-active"
        flag.parent.mkdir(parents=True, exist_ok=True)
        if mode:
            flag.write_text(mode)
        elif flag.exists():
            flag.unlink()

        env = os.environ.copy()
        env["HOME"] = str(home)
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "hooks" / "caveman-statusline.sh")],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        return result.stdout

    def strip_ansi(self, text):
        import re
        return re.sub(r'\033\[[^m]*m', '', text)

    def test_full_badge(self):
        with tempfile.TemporaryDirectory(prefix="caveman-sl-full-") as tmp:
            out = self.run_statusline("full", tmp)
            self.assertIn("[CAVEMAN]", self.strip_ansi(out))
            self.assertNotIn("[CAVEMAN:FULL]", self.strip_ansi(out))

    def test_lite_badge(self):
        with tempfile.TemporaryDirectory(prefix="caveman-sl-lite-") as tmp:
            out = self.run_statusline("lite", tmp)
            self.assertIn("[CAVEMAN:LITE]", self.strip_ansi(out))

    def test_ultra_badge(self):
        with tempfile.TemporaryDirectory(prefix="caveman-sl-ultra-") as tmp:
            out = self.run_statusline("ultra", tmp)
            self.assertIn("[CAVEMAN:ULTRA]", self.strip_ansi(out))

    def test_commit_badge(self):
        with tempfile.TemporaryDirectory(prefix="caveman-sl-commit-") as tmp:
            out = self.run_statusline("commit", tmp)
            self.assertIn("[CAVEMAN:COMMIT]", self.strip_ansi(out))

    def test_empty_flag_no_output(self):
        with tempfile.TemporaryDirectory(prefix="caveman-sl-empty-") as tmp:
            out = self.run_statusline(None, tmp)
            self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
