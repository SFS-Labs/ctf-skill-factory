import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gateway

CYBER = {
    "id": "bench-01",
    "name": "Known incident",
    "chain": "bsc",
    "block_number": 12653565,
    "vulnerable_address": "0xf642f2a626a8b732619606c493abfc2433dd2d35",
    "function": "_calculateSwap",
    "type": "accounting-error",
    "file": "MetaSwapUtils.sol",
    "fix_description": "SECRET FIX",
    "attack_txs": ["0xattack"],
    "case_link": "https://incident",
}
CONFIG = """id: 2023-07-pooltogether
framework: foundry-json
run_cmd_dir: vault
base_commit: 4240445ed3b5145be1032cf1becc9c6866046bf7
vulnerabilities:
  - id: "H-02"
    title: "SECRET vulnerability"
"""
DOCKERFILE = "RUN git clone --recurse https://github.com/evmbench-org/2023-07-pooltogether.git $AUDIT_DIR"


def mocked(source, path):
    if source == "cyberchainbench":
        return json.dumps(CYBER)
    return DOCKERFILE if path.endswith("Dockerfile") else CONFIG


class GatewayTest(unittest.TestCase):
    def test_cyber_detect_masks_known_answer(self):
        with patch.object(gateway, "fetch_text", side_effect=mocked):
            brief = gateway.prepare("cyberchainbench", "bench-01", "detect")
        output = json.dumps(brief)
        for secret in (
            "_calculateSwap", "accounting-error", "SECRET FIX",
            "0xattack", "Known incident", "bench-01", "12653565",
        ):
            self.assertNotIn(secret, output)
        self.assertEqual(brief["target"]["chain"], "bsc")

    def test_cyber_reproduce_adds_block_not_solution(self):
        with patch.object(gateway, "fetch_text", side_effect=mocked):
            brief = gateway.prepare("cyberchainbench", "bench-01", "reproduce")
        self.assertEqual(brief["target"]["historical_block"], 12653565)
        self.assertNotIn("_calculateSwap", json.dumps(brief))

    def test_reevm_masks_finding(self):
        with patch.object(gateway, "fetch_text", side_effect=mocked):
            brief = gateway.prepare("reevmbench", "2023-07-pooltogether", "detect")
        self.assertNotIn("H-02", json.dumps(brief))
        self.assertNotIn("SECRET", json.dumps(brief))
        self.assertEqual(
            brief["target"]["source_commit"],
            "4240445ed3b5145be1032cf1becc9c6866046bf7",
        )

    def test_cyber_grade(self):
        with patch.object(gateway, "fetch_text", side_effect=mocked):
            good = gateway.grade("cyberchainbench", "bench-01", {
                "findings": [{"type": "ACCOUNTING-ERROR", "function": "_calculateSwap"}]
            })
            bad = gateway.grade("cyberchainbench", "bench-01", {
                "findings": [{"type": "reentrancy", "function": "withdraw"}]
            })
        self.assertEqual(good["status"], "LABEL_MATCH_UNVERIFIED")
        self.assertFalse(bad["label_match"])
        self.assertEqual(good["independent_reproduction"], "NOT_VERIFIED")

    def test_reevm_grade(self):
        with patch.object(gateway, "fetch_text", side_effect=mocked):
            result = gateway.grade("reevmbench", "2023-07-pooltogether", {
                "findings": [{"finding_id": "H-02"}]
            })
        self.assertEqual(result["status"], "ID_MATCH_UNVERIFIED")

    def test_path_rejection(self):
        for bad in ("../../secret", "../bench-01", "foo/bar", "", ".hidden", "a;b"):
            with self.assertRaises(gateway.GatewayError):
                gateway.validate_id(bad)
        with self.assertRaises(gateway.GatewayError):
            gateway.confined_submission_path("../../README.md")


if __name__ == "__main__":
    unittest.main()
