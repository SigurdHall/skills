import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "skills"
    / "reporting"
    / "orchestration"
    / "design-bi-report-wireframes"
    / "scripts"
    / "validate_story_frame.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("validate_story_frame", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_payload() -> dict:
    return {
        "contract": "StoryFrameV1-draft",
        "status": "exploratory-pending-evidence",
        "dataState": "synthetic",
        "sourceRefs": {
            "storyBrief": "brief:test:v1",
            "narrativeEvidence": "evidence:test:v1",
            "contentHash": "sha256:test-hash",
            "brandIntentRef": "brand:test:v1",
            "tasteProfileRef": "taste:test:v1",
        },
        "frames": [
            {
                "frameId": "overview",
                "order": 1,
                "decisionQuestion": "Where is action needed?",
                "keyClaimRef": "claim:material-variance:pending",
                "evidenceNeeds": [
                    {
                        "intent": "compare_actual_to_baseline",
                        "priority": "primary",
                        "semanticRoleRefs": ["measure:actual", "measure:baseline"],
                        "factRefs": ["fact:certified-total:pending"],
                    }
                ],
                "comparisonContext": {"baseline": "approved-plan"},
                "driverStatus": "required",
                "caveats": [],
                "freshnessRequirement": "show-source-timestamp",
                "nextAction": "inspect-largest-variance",
                "traceRefs": [
                    "brief:test:v1",
                    "evidence:test:v1",
                    "sha256:test-hash",
                    "brand:test:v1",
                    "taste:test:v1",
                ],
            }
        ],
    }


class StoryFrameValidatorTests(unittest.TestCase):
    def test_accepts_minimum_pending_evidence_envelope(self) -> None:
        module = load_module()

        self.assertEqual(module.validate_payload(valid_payload()), [])

    def test_rejects_duplicate_ids_geometry_and_unmarked_pending_refs(self) -> None:
        module = load_module()
        payload = valid_payload()
        payload["status"] = "exploratory"
        payload["dataState"] = "unknown"
        payload["frames"][0]["keyClaimRef"] = "claim:material-variance"
        payload["frames"][0]["x"] = 20
        payload["frames"][0]["position"] = {"left": 20, "top": 10}
        payload["frames"][0]["pixelOffset"] = 12
        duplicate = dict(payload["frames"][0])
        duplicate["order"] = 2
        payload["frames"].append(duplicate)

        errors = module.validate_payload(payload)

        self.assertTrue(any("Duplicate frameId" in error for error in errors))
        self.assertTrue(any("forbidden target key 'x'" in error for error in errors))
        self.assertTrue(any("forbidden target key 'position'" in error for error in errors))
        self.assertTrue(any("unexpected field 'pixelOffset'" in error for error in errors))
        self.assertTrue(any("unsupported status" in error for error in errors))
        self.assertTrue(any("unsupported dataState" in error for error in errors))
        self.assertTrue(any("must be marked pending" in error for error in errors))

    def test_rejects_hidden_target_fields_and_invalid_trace_or_brand_refs(self) -> None:
        module = load_module()
        payload = valid_payload()
        payload["sourceRefs"]["brandIntentRef"] = "untyped-brand"
        payload["frames"][0]["traceRefs"] = ["brief:test:v1", "evidence:other:v1"]
        payload["frames"][0]["comparisonContext"]["pixelOffset"] = 12
        payload["frames"][0]["comparisonContext"]["period"] = {"cssGridColumns": 3}
        payload["frames"][0]["caveats"] = [{"xCoordinate": 20}]

        errors = module.validate_payload(payload)

        self.assertTrue(any("brandIntentRef: expected a 'brand:' reference" in error for error in errors))
        self.assertTrue(any("traceRefs: missing source reference" in error for error in errors))
        self.assertTrue(any("traceRefs: reference is not declared" in error for error in errors))
        self.assertTrue(any("comparisonContext: unexpected field 'pixelOffset'" in error for error in errors))
        self.assertTrue(any("comparisonContext.period: expected a primitive value" in error for error in errors))
        self.assertTrue(any("caveats: expected a list of strings" in error for error in errors))
        self.assertTrue(any("forbidden target key 'cssGridColumns'" in error for error in errors))
        self.assertTrue(any("forbidden target key 'xCoordinate'" in error for error in errors))

    def test_accepts_hash_locked_knowledge_only_context(self) -> None:
        module = load_module()
        payload = valid_payload()
        payload["dataState"] = "knowledge_only_no_values"
        payload["knowledgeContext"] = {
            "selectionId": "selection.finance.reference.abcdef123456",
            "selectionSha256": "a" * 64,
            "registrySnapshotSha256": "b" * 64,
            "selectedDomainRefs": ["domain.finance.statements"],
            "unresolvedKnowledgeRequirements": [],
            "evidenceAdvisories": ["candidate_record:report.finance"],
        }

        self.assertEqual(module.validate_payload(payload), [])

    def test_rejects_malformed_knowledge_context(self) -> None:
        module = load_module()
        payload = valid_payload()
        payload["knowledgeContext"] = {
            "selectionId": "invalid selection",
            "selectionSha256": "short",
            "registrySnapshotSha256": "b" * 64,
            "selectedDomainRefs": ["domain.finance.statements", "domain.finance.statements"],
            "unresolvedKnowledgeRequirements": [""],
            "evidenceAdvisories": [""],
        }

        errors = module.validate_payload(payload)

        self.assertTrue(any("selectionId" in error for error in errors))
        self.assertTrue(any("selectionSha256" in error for error in errors))
        self.assertTrue(any("duplicate reference" in error for error in errors))
        self.assertTrue(any("unresolvedKnowledgeRequirements" in error for error in errors))
        self.assertTrue(any("evidenceAdvisories" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
