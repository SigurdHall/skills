import sys
import unittest
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "reporting"
    / "powerbi"
    / "powerbi-pbip"
    / "scripts"
)
FIXTURE_DIR = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "powerbi-bookmark-actions"
    / "definition"
)
sys.path.insert(0, str(SCRIPT_DIR))

from validate_bookmark_actions import find_bookmark_action_issues


class PowerBiPbipToolTests(unittest.TestCase):
    def test_bookmark_action_validator_reports_cross_page_bookmark_targets(self):
        issues = find_bookmark_action_issues(FIXTURE_DIR)

        self.assertEqual(1, len(issues))
        self.assertIn("Current page/button_1", issues[0])
        self.assertIn("activeSection=other_page", issues[0])


if __name__ == "__main__":
    unittest.main()
