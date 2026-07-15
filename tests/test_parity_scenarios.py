import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    REPO_ROOT
    / "skills"
    / "reporting"
    / "orchestration"
    / "design-bi-report-wireframes"
    / "assets"
    / "parity-scenarios.example.json"
)


class ParityScenarioTests(unittest.TestCase):
    def test_finance_example_expected_values_match_declared_conventions(self) -> None:
        payload = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        cases = {case["caseId"]: case for case in payload["cases"]}
        self.assertTrue(
            {
                "cost-over-budget",
                "revenue-over-budget",
                "zero-budget",
                "incomplete-period",
                "unexplained-driver-residual",
                "missing-input",
            }.issubset(cases)
        )

        for case in cases.values():
            inputs = case["input"]
            expected = case["expected"]
            actual = inputs["actual"]
            budget = inputs["budget"]
            if actual is None or budget is None:
                self.assertEqual(
                    expected,
                    {
                        "varianceAmount": None,
                        "variancePercent": None,
                        "favorable": None,
                        "driverResidual": None,
                        "comparisonStatus": "missing-input",
                    },
                )
                continue

            variance = actual - budget
            variance_percent = None if budget == 0 else variance / abs(budget)
            favorable = (
                variance <= 0
                if inputs["measureDirection"] == "cost"
                else variance >= 0
            )
            residual = variance - sum(inputs["driverContributions"])
            if budget == 0:
                status = "zero-baseline"
            elif inputs["periodStatus"] != "complete":
                status = "incomplete-period-warning"
            elif residual != 0:
                status = "unreconciled-drivers"
            else:
                status = "comparable"

            self.assertEqual(expected["varianceAmount"], variance)
            self.assertEqual(expected["variancePercent"], variance_percent)
            self.assertEqual(expected["favorable"], favorable)
            self.assertEqual(expected["driverResidual"], residual)
            self.assertEqual(expected["comparisonStatus"], status)


if __name__ == "__main__":
    unittest.main()
