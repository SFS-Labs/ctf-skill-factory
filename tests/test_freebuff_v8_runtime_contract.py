"""Contract tests for the project-local, noncolliding Freebuff V8 skill.

These tests validate repository packaging, NOT a Freebuff desktop skill load.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
V8_PROJECT_SKILL = ROOT / ".agents/skills/ctf-skill-index-v8/SKILL.md"
V8_SOURCE = ROOT / "skill/ctf-skill-index.SKILL.md"


class FreebuffV8ProjectSkillTests(unittest.TestCase):
    def test_frontmatter_name_matches_directory(self):
        body = V8_PROJECT_SKILL.read_text(encoding="utf-8")
        self.assertTrue(body.startswith("---\nname: ctf-skill-index-v8\n"))
        self.assertEqual(V8_PROJECT_SKILL.parent.name, "ctf-skill-index-v8")

    def test_project_skill_is_v8_source_with_only_name_changed(self):
        installed = V8_PROJECT_SKILL.read_text(encoding="utf-8")
        source = V8_SOURCE.read_text(encoding="utf-8")
        self.assertTrue(source.startswith("---\nname: ctf-skill-index\n"))
        expected = source.replace(
            "---\nname: ctf-skill-index\n",
            "---\nname: ctf-skill-index-v8\n",
            1,
        )
        self.assertEqual(installed, expected)
        self.assertIn("bin/skill-orchestrator.py", installed)

    def test_installer_targets_project_directory_and_preserves_legacy(self):
        installer = (ROOT / "install-freebuff.sh").read_text(encoding="utf-8")
        self.assertIn('V8_PROJECT_TARGET="$ROOT/.agents/skills/ctf-skill-index-v8"', installer)
        self.assertIn('put "$V8_SKILL_SOURCE" "$V8_PROJECT_TARGET/SKILL.md" 644', installer)
        self.assertIn('TARGET="${FREEBUFF_SKILL_DIR:-$HOME/.agents/skills/ctf-skill-index}"', installer)
        self.assertNotIn("rm -rf", installer)

    def test_agent_instructions_reference_correct_v8_skill(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("ctf-skill-index-v8", text)
        self.assertIn("bin/skill-orchestrator.py", text)


if __name__ == "__main__":
    unittest.main()
