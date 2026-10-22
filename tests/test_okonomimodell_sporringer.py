import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "reporting"
    / "powerbi"
    / "okonomimodell-sporringer"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

import okonomimodell_dax as modul  # noqa: E402
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


class F8GodkjenningTests(unittest.TestCase):
    DAX = 'EVALUATE ROW ( "a", 1 )'

    def rad(self, mal=None, klasse_="S", alder=3600.0, naa=None) -> dict:
        rad = {"noekkel": noekkel(self.DAX), "klasse": klasse_, "tid": (naa or time.time()) - alder}
        if mal is not None:
            rad["mal"] = mal
        return rad

    def test_mapping_from_f8_target_to_ppu_target_is_explicit(self) -> None:
        self.assertEqual({"f8": "ppu", "bevcontroller-f8": "bevcontroller"}, modul.F8_GODKJENNES_MOT)

    def test_bevcontroller_f8_requires_class_s_on_bevcontroller(self) -> None:
        naa = time.time()
        logg = [self.rad("bevcontroller", naa=naa)]

        self.assertTrue(godkjent_for_f8(self.DAX, logg, naa, "bevcontroller"))

    def test_bevcontroller_f8_is_not_approved_by_a_ppu_run(self) -> None:
        naa = time.time()

        self.assertFalse(godkjent_for_f8(self.DAX, [self.rad("ppu", naa=naa)], naa, "bevcontroller"))
        self.assertFalse(godkjent_for_f8(self.DAX, [self.rad(naa=naa)], naa, "bevcontroller"))

    def test_f8_is_not_approved_by_a_bevcontroller_run(self) -> None:
        naa = time.time()

        self.assertFalse(godkjent_for_f8(self.DAX, [self.rad("bevcontroller", naa=naa)], naa, "ppu"))
        self.assertFalse(godkjent_for_f8(self.DAX, [self.rad("bevcontroller", naa=naa)], naa))

    def test_f8_still_approves_old_log_rows_without_mal(self) -> None:
        naa = time.time()
        gammel_rad = self.rad(naa=naa)

        self.assertNotIn("mal", gammel_rad)
        self.assertTrue(godkjent_for_f8(self.DAX, [gammel_rad], naa))
        self.assertTrue(godkjent_for_f8(self.DAX, [gammel_rad], naa, "ppu"))

    def test_bevcontroller_f8_keeps_the_class_and_age_rules(self) -> None:
        naa = time.time()

        self.assertFalse(godkjent_for_f8(self.DAX, [self.rad("bevcontroller", "M", naa=naa)], naa, "bevcontroller"))
        self.assertFalse(
            godkjent_for_f8(self.DAX, [self.rad("bevcontroller", alder=8 * 86400, naa=naa)], naa, "bevcontroller")
        )


class BlokkOkTests(unittest.TestCase):
    def test_error_is_not_ok(self) -> None:
        self.assertFalse(modul.blokk_ok({"feil": "Resource Governance", "alle": None}))
        self.assertFalse(modul.blokk_ok({"feil": "feil", "alle": [{"[ok]": True}]}))

    def test_false_in_one_row_is_not_ok(self) -> None:
        svar = {"feil": None, "alle": [{"[ok]": True}, {"[ok]": False}, {"[ok]": True}]}

        self.assertFalse(modul.blokk_ok(svar))

    def test_zero_counts_as_false(self) -> None:
        self.assertFalse(modul.blokk_ok({"feil": None, "alle": [{"[ok]": 0}]}))

    def test_all_true_is_ok(self) -> None:
        self.assertTrue(modul.blokk_ok({"feil": None, "alle": [{"[ok]": True}, {"[ok]": True}]}))
        self.assertTrue(modul.blokk_ok({"feil": None, "alle": [{"[ok]": 1}]}))

    def test_rows_without_ok_column_are_ok(self) -> None:
        self.assertTrue(modul.blokk_ok({"feil": None, "alle": [{"[a]": 0}, {"[a]": False}]}))

    def test_no_rows_is_ok(self) -> None:
        self.assertTrue(modul.blokk_ok({"feil": None, "alle": []}))
        self.assertTrue(modul.blokk_ok({"feil": None, "alle": None}))


class KonfigStiTests(unittest.TestCase):
    def test_env_var_overrides_config_path(self) -> None:
        with mock.patch.dict(os.environ, {"OKONOMIMODELL_KONFIG": str(Path("x") / "min.json")}):
            self.assertEqual(Path("x") / "min.json", modul.konfig_sti())

    def test_default_path_without_env_var(self) -> None:
        miljo = {k: v for k, v in os.environ.items() if k != "OKONOMIMODELL_KONFIG"}
        with mock.patch.dict(os.environ, miljo, clear=True):
            self.assertEqual(modul.KONFIG, modul.konfig_sti())

    def test_empty_env_var_uses_default_path(self) -> None:
        with mock.patch.dict(os.environ, {"OKONOMIMODELL_KONFIG": ""}):
            self.assertEqual(modul.KONFIG, modul.konfig_sti())


class MainTests(unittest.TestCase):
    """Kjører main() mot en falsk kjor_dax. Ingen nettkall, ingen token."""

    MAL = ["ppu", "ledelse", "f8", "bevcontroller", "bevcontroller-f8"]
    OK = 'EVALUATE ROW ( "ok", TRUE ( ) )'
    FEIL_RAD = 'EVALUATE ROW ( "ok", FALSE ( ) )'
    FEIL_SVAR = "EVALUATE FEILER"
    DAX_FIL = f"-- K01 ok\n{OK}\n\n-- K02 ok-kolonne false\n{FEIL_RAD}\n\n-- K03 feiler\n{FEIL_SVAR}\n\n-- K04 ok igjen\n{OK}\n"

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.ko = self.tmp / "ko"
        self.ut = self.tmp / "ut"
        self.fil = self.tmp / "sporringer.dax"
        self.fil.write_text(self.DAX_FIL, encoding="utf-8")
        self.konfig = self.tmp / "konfig.json"
        self.skriv_konfig(self.MAL)
        self.kall: list[tuple[str, str, str]] = []

        def falsk_kjor_dax(token, ws, ds, dax):
            self.kall.append((ws, ds, dax))
            if dax == self.FEIL_SVAR:
                return {"sekunder": 0.1, "rader": None, "forste": [], "alle": None, "feil": "feil"}
            rader = [{"[ok]": dax != self.FEIL_RAD}]
            return {"sekunder": 0.1, "rader": 1, "forste": rader, "alle": rader, "feil": None}

        for patch in (
            mock.patch.object(modul, "KO", self.ko),
            mock.patch.object(modul, "PPU_LOGG", self.ko / "ppu_logg.jsonl"),
            mock.patch.object(modul, "F8_PAUSE", 0.0),
            mock.patch.object(modul, "hent_token", lambda: "token"),
            mock.patch.object(modul, "kjor_dax", falsk_kjor_dax),
            mock.patch.dict(os.environ, {"OKONOMIMODELL_KONFIG": str(self.konfig)}),
        ):
            patch.start()
            self.addCleanup(patch.stop)

    def skriv_konfig(self, mal: list[str]) -> None:
        self.konfig.write_text(
            json.dumps({m: {"workspace": f"ws-{m}", "dataset": f"ds-{m}", "navn": m} for m in mal}),
            encoding="utf-8",
        )

    def kjor(self, *argv: str) -> tuple[int, str, str]:
        ut, feil = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(ut), contextlib.redirect_stderr(feil):
            rc = modul.main([*argv, "--fil", str(self.fil), "--ut", str(self.ut)])
        return rc, ut.getvalue(), feil.getvalue()

    def logg(self) -> list[dict]:
        return [json.loads(rad) for rad in (self.ko / "ppu_logg.jsonl").read_text(encoding="utf-8").splitlines()]

    def teller(self) -> int:
        return json.loads(modul.f8_teller_sti().read_text())["kall"]

    def test_config_is_read_from_env_var_and_used_per_target(self) -> None:
        rc, _, _ = self.kjor("--mal", "bevcontroller", "K01")

        self.assertEqual(0, rc)
        self.assertEqual([("ws-bevcontroller", "ds-bevcontroller", self.OK)], self.kall)

    def test_missing_config_file_is_reported(self) -> None:
        self.konfig.unlink()

        rc, _, feil = self.kjor("--mal", "ppu")

        self.assertEqual(2, rc)
        self.assertIn(str(self.konfig), feil)
        self.assertEqual([], self.kall)

    def test_missing_target_message_is_generic(self) -> None:
        self.skriv_konfig(["ppu"])

        rc, _, feil = self.kjor("--mal", "bevcontroller-f8")

        self.assertEqual(2, rc)
        self.assertIn("'bevcontroller-f8'", feil)
        self.assertIn("workspace", feil)
        self.assertIn("dataset", feil)
        self.assertIn("navn", feil)
        self.assertNotIn("fase 10", feil.lower())
        self.assertEqual([], self.kall)

    def test_new_targets_are_valid_choices(self) -> None:
        for mal in ("bevcontroller", "bevcontroller-f8"):
            with self.subTest(mal=mal):
                self.skriv_konfig(["ppu"])
                rc, _, _ = self.kjor("--mal", mal)
                self.assertEqual(2, rc)  # 2 = mangler i konfigurasjonen. Ugyldig valg ville gitt SystemExit.

    def test_ppu_and_bevcontroller_runs_are_logged_with_mal(self) -> None:
        self.kjor("--mal", "ppu", "K01")
        self.kjor("--mal", "bevcontroller", "K04")

        rader = self.logg()

        self.assertEqual(["ppu", "bevcontroller"], [r["mal"] for r in rader])
        self.assertEqual(["K01", "K04"], [r["kode"] for r in rader])

    def test_ledelse_runs_are_not_logged(self) -> None:
        self.kjor("--mal", "ledelse", "K01")

        self.assertFalse((self.ko / "ppu_logg.jsonl").exists())

    def test_bevcontroller_f8_runs_only_what_ran_as_s_on_bevcontroller(self) -> None:
        self.kjor("--mal", "bevcontroller", "K01")
        self.kall.clear()

        rc, _, _ = self.kjor("--mal", "bevcontroller-f8", "K01")

        self.assertEqual(0, rc)
        self.assertEqual([("ws-bevcontroller-f8", "ds-bevcontroller-f8", self.OK)], self.kall)

    def test_bevcontroller_f8_is_rejected_when_only_logged_on_ppu(self) -> None:
        self.kjor("--mal", "ppu", "K01")
        self.kall.clear()

        rc, _, feil = self.kjor("--mal", "bevcontroller-f8", "K01")

        self.assertEqual(3, rc)
        self.assertIn("bevcontroller", feil)
        self.assertEqual([], self.kall)

    def test_f8_is_rejected_when_only_logged_on_bevcontroller(self) -> None:
        self.kjor("--mal", "bevcontroller", "K01")
        self.kall.clear()

        rc, _, _ = self.kjor("--mal", "f8", "K01")

        self.assertEqual(3, rc)
        self.assertEqual([], self.kall)

    def test_f8_still_accepts_old_log_rows_without_mal(self) -> None:
        self.ko.mkdir()
        (self.ko / "ppu_logg.jsonl").write_text(
            json.dumps({"noekkel": noekkel(self.OK), "kode": "K01", "klasse": "S", "sekunder": 0.2, "tid": time.time()}) + "\n",
            encoding="utf-8",
        )

        rc, _, _ = self.kjor("--mal", "f8", "K01")

        self.assertEqual(0, rc)
        self.assertEqual([("ws-f8", "ds-f8", self.OK)], self.kall)

    def test_both_f8_targets_share_the_same_daily_counter_file(self) -> None:
        self.kjor("--mal", "ppu", "K01")
        self.kjor("--mal", "bevcontroller", "K01")

        self.assertEqual(0, self.kjor("--mal", "f8", "K01")[0])
        self.assertEqual(1, self.teller())
        self.assertEqual(0, self.kjor("--mal", "bevcontroller-f8", "K01")[0])
        self.assertEqual(2, self.teller())
        self.assertEqual(1, len(list(self.ko.glob("okonomimodell_f8_*.json"))))

    def test_f8_budget_of_five_is_split_between_both_targets(self) -> None:
        self.kjor("--mal", "ppu", "K01")
        self.kjor("--mal", "bevcontroller", "K01")
        for _ in range(3):
            self.assertEqual(0, self.kjor("--mal", "f8", "K01")[0])
        for _ in range(2):
            self.assertEqual(0, self.kjor("--mal", "bevcontroller-f8", "K01")[0])
        kall_for = len(self.kall)

        rc_f8, _, feil_f8 = self.kjor("--mal", "f8", "K01")
        rc_bev, _, feil_bev = self.kjor("--mal", "bevcontroller-f8", "K01")

        self.assertEqual((4, 4), (rc_f8, rc_bev))
        self.assertIn("5 av 5", feil_f8)
        self.assertIn("5 av 5", feil_bev)
        self.assertEqual(kall_for, len(self.kall))

    def test_without_forvent_exit_code_is_zero_even_when_blocks_fail(self) -> None:
        rc, ut, feil = self.kjor("--mal", "ppu")

        self.assertEqual(0, rc)
        self.assertEqual(4, len(ut.strip().splitlines()))
        self.assertEqual("", feil)

    def test_forvent_returns_1_when_a_block_fails_and_runs_all_blocks(self) -> None:
        rc, ut, feil = self.kjor("--mal", "ppu", "--forvent")

        self.assertEqual(1, rc)
        self.assertEqual(4, len(ut.strip().splitlines()))
        self.assertEqual(4, len(self.kall))
        linjer = feil.strip().splitlines()
        self.assertEqual(1, len(linjer))
        self.assertIn("K02", linjer[0])
        self.assertIn("K03", linjer[0])
        self.assertNotIn("K01", linjer[0])
        self.assertNotIn("K04", linjer[0])

    def test_forvent_returns_1_for_ok_false_in_a_row(self) -> None:
        rc, _, feil = self.kjor("--mal", "ppu", "--forvent", "K02")

        self.assertEqual(1, rc)
        self.assertIn("K02", feil)

    def test_forvent_returns_1_for_error_only(self) -> None:
        rc, _, feil = self.kjor("--mal", "ppu", "--forvent", "K03")

        self.assertEqual(1, rc)
        self.assertIn("K03", feil)

    def test_forvent_returns_0_and_is_silent_when_all_blocks_pass(self) -> None:
        rc, _, feil = self.kjor("--mal", "ppu", "--forvent", "K01", "K04")

        self.assertEqual(0, rc)
        self.assertEqual("", feil)


if __name__ == "__main__":
    unittest.main()
