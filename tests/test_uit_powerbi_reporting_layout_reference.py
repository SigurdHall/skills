import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1] / "skills" / "reporting" / "norms" / "uit-powerbi-reporting"


class UitPowerBiReportingLayoutReferenceTests(unittest.TestCase):
    def test_uit_powerbi_reporting_has_layout_catalog_reference(self) -> None:
        reference = SKILL_ROOT / "references" / "public" / "okonomi-template-layouts-all.html"

        self.assertTrue(reference.exists())
        text = reference.read_text(encoding="utf-8")
        self.assertIn("okonomi-template-layouts-all", reference.name)
        self.assertNotIn("Forelopig budsjettfordeling", text)
        self.assertNotIn("pSourceWorkbookPath", text)

    def test_uit_powerbi_reporting_skill_mentions_layout_catalog(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("references/public/okonomi-template-layouts-all.html", skill_text)
        self.assertIn("layoutkatalog", skill_text.lower())


if __name__ == "__main__":
    unittest.main()
