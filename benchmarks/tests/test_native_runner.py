"""Boundary tests for native upstream runner; no benchmark/model/network execution."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "run-native-exploit.sh"


class NativeRunnerBoundaryTests(unittest.TestCase):
    def call(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCRIPT), *arguments],
            capture_output=True, text=True, timeout=5, check=False,
        )

    def test_shell_parses(self):
        check = subprocess.run(["bash", "-n", str(SCRIPT)],
                               capture_output=True, text=True, timeout=5)
        self.assertEqual(check.returncode, 0, check.stderr)

    def test_cyber_score_fails_before_download_without_candidate(self):
        outcome = self.call("score", "cyberchainbench", "bench-01")
        self.assertEqual(outcome.returncode, 3, outcome.stderr)
        self.assertIn("frozen .sol", outcome.stderr)

    def test_reevm_score_fails_before_download_without_candidate(self):
        outcome = self.call("score", "reevmbench", "2023-07-pooltogether")
        self.assertEqual(outcome.returncode, 3, outcome.stderr)
        self.assertIn("frozen .sh", outcome.stderr)

    def test_case_id_prevents_path_traversal(self):
        outcome = self.call("score", "cyberchainbench", "../../secrets")
        self.assertEqual(outcome.returncode, 2)
        self.assertIn("Invalid case ID", outcome.stderr)

    def test_unsupported_source_does_not_start_download(self):
        outcome = self.call("score", "not-a-source", "bench-01")
        self.assertEqual(outcome.returncode, 2)
        self.assertIn("Unsupported source", outcome.stderr)


if __name__ == "__main__":
    unittest.main()
