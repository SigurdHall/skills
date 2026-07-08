import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORTING_ROOT = REPO_ROOT / "skills" / "reporting"
UIT_REPORTING_ROOT = REPORTING_ROOT / "norms" / "uit-powerbi-reporting"


class ReportingSensitiveReferencesTests(unittest.TestCase):
    def public_text_files(self) -> list[Path]:
        files: list[Path] = []
        for path in REPORTING_ROOT.rglob("*"):
            if not path.is_file():
                continue
            parts = set(path.parts)
            if "assets" in parts or "references" in parts and "private" in parts:
                continue
            if path.suffix.lower() in {".md", ".yaml", ".yml"} or path.name == "SKILL.md":
                files.append(path)
        return files

    def test_private_business_logic_lives_under_ignored_references_private(self) -> None:
        private_reference = (
            UIT_REPORTING_ROOT
            / "references"
            / "private"
            / "uit-okonomi-og-strategi-forretningslogikk.md"
        )

        self.assertTrue(private_reference.exists())
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "check-ignore", str(private_reference)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_public_reporting_skill_text_has_no_internal_examples(self) -> None:
        forbidden = [
            "references/uit-okonomi-og-strategi-forretningslogikk.md",
            "340320",
            "2627",
            "BFE-fartøydrift",
            "BEA",
            "C:\\repos\\private",
            "private/Vault",
        ]

        hits: list[str] = []
        for path in self.public_text_files():
            text = path.read_text(encoding="utf-8")
            for needle in forbidden:
                if needle in text:
                    hits.append(f"{path.relative_to(REPO_ROOT)}: {needle}")

        self.assertEqual(hits, [])

    def test_reporting_references_are_split_into_public_or_private(self) -> None:
        direct_reference_files = [
            path.relative_to(REPO_ROOT)
            for path in REPORTING_ROOT.rglob("references/*")
            if path.is_file()
        ]

        self.assertEqual(direct_reference_files, [])


if __name__ == "__main__":
    unittest.main()
