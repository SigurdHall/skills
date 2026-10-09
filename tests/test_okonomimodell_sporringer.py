import sys
import time
import unittest
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "reporting"
    / "powerbi"
    / "okonomimodell-sporringer"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from okonomimodell_dax import godkjent_for_f8, klasse, les_blokker, noekkel  # noqa: E402


class OkonomimodellSporringerTests(unittest.TestCase):
    def test_reads_blocks_with_codes(self) -> None:
        tekst = "-- K01 Skalar.\nEVALUATE ROW ( \"a\", 1 )\n\n-- K02 Per år.\nEVALUATE\nVALUES ( t[c] )\n"

        self.assertEqual(
            [("K01", 'EVALUATE ROW ( "a", 1 )'), ("K02", "EVALUATE\nVALUES ( t[c] )")],
            les_blokker(tekst),
        )

    def test_class_follows_ppu_time_rows_and_error(self) -> None:
        self.assertEqual("S", klasse(0.6, 416, None))
        self.assertEqual("M", klasse(0.6, 501, None))
        self.assertEqual("M", klasse(3.8, 1, None))
        self.assertEqual("L", klasse(38.9, 1, None))
        self.assertEqual("X", klasse(106.0, None, "Resource Governance"))

    def test_key_ignores_whitespace(self) -> None:
        self.assertEqual(noekkel("EVALUATE  ROW ( 1 )"), noekkel("EVALUATE\nROW ( 1 )"))

    def test_f8_requires_recent_class_s_run_on_ppu(self) -> None:
        dax = "EVALUATE ROW ( \"a\", 1 )"
        naa = time.time()
        fersk_s = {"noekkel": noekkel(dax), "klasse": "S", "tid": naa - 3600}
        gammel_s = {"noekkel": noekkel(dax), "klasse": "S", "tid": naa - 8 * 86400}
        fersk_m = {"noekkel": noekkel(dax), "klasse": "M", "tid": naa - 3600}

        self.assertTrue(godkjent_for_f8(dax, [fersk_s], naa))
        self.assertFalse(godkjent_for_f8(dax, [gammel_s], naa))
        self.assertFalse(godkjent_for_f8(dax, [fersk_m], naa))
        self.assertFalse(godkjent_for_f8(dax, [], naa))


if __name__ == "__main__":
    unittest.main()
