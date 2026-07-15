import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP_ROOT = REPO_ROOT / ".tmp-tests"
SCRIPT = (
    REPO_ROOT
    / "skills"
    / "reporting"
    / "orchestration"
    / "design-bi-report-wireframes"
    / "scripts"
    / "analyze_measure_corpus.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("analyze_measure_corpus", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class MeasureCorpusAnalyzerTests(unittest.TestCase):
    def temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT, ignore_cleanup_errors=True)

    def test_parses_supported_formats_and_excludes_non_measures(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            root = Path(tmpdir)
            source_a = root / "source-a"
            source_b = root / "source-b"
            (source_a / "Model" / "tables").mkdir(parents=True)
            (source_b / "tables" / "Sales" / "measures").mkdir(parents=True)
            (source_b / "tables" / "Metric" / "calculationItems").mkdir(parents=True)

            (source_a / "Model" / "tables" / "Sales.tmdl").write_text(
                """table Sales
\tmeasure 'Sales Amount' = SUMX ( Sales, Sales[Quantity] * Sales[Price] )
\t\tformatString: #,0

\tmeasure 'Sales YTD' =
\t\tCALCULATE (
\t\t\t[Sales Amount],
\t\t\tDATESYTD ( 'Date'[Date] )
\t\t)
\t\tformatString: #,0

\tmeasure Ratio = ```
\t\tDIVIDE ( [Profit], [Sales Amount] )
\t\t```

\tcolumn 'Calculated Label' = FORMAT ( [Sales Amount], "#,0" )
""",
                encoding="utf-8",
            )
            (source_a / "model.bim").write_text(
                json.dumps(
                    {
                        "model": {
                            "tables": [
                                {
                                    "name": "Sales",
                                    "measures": [
                                        {"name": "Total Sales", "expression": "SUM ( Sales[Amount] )"},
                                        {
                                            "name": "Unique Customers",
                                            "expression": "DISTINCTCOUNT ( Sales[CustomerKey] )",
                                        },
                                    ],
                                    "columns": [
                                        {"name": "Calculated", "expression": "RELATED ( Product[Name] )"}
                                    ],
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            (source_b / "tables" / "Sales" / "measures" / "Margin.json").write_text(
                json.dumps({"name": "Margin %", "expression": "DIVIDE ( [Profit], [Sales] )"}),
                encoding="utf-8",
            )
            (source_b / "tables" / "Sales" / "measures" / "Sales Amount Copy.json").write_text(
                json.dumps(
                    {
                        "name": "Sales Amount Copy",
                        "expression": "SUMX(Sales, Sales[Quantity] * Sales[Price])",
                    }
                ),
                encoding="utf-8",
            )
            (
                source_b / "tables" / "Metric" / "calculationItems" / "YTD.json"
            ).write_text(
                json.dumps({"name": "YTD", "expression": "CALCULATE(SELECTEDMEASURE(), DATESYTD('Date'[Date]))"}),
                encoding="utf-8",
            )

            result = module.analyze_paths([source_a, source_b])

            self.assertEqual(result["corpus"]["measure_instances"], 7)
            self.assertEqual(result["corpus"]["unique_expressions"], 6)
            self.assertEqual(result["corpus"]["calculation_items_excluded"], 1)
            self.assertEqual(result["functions"]["SUMX"]["measure_instances"], 2)
            self.assertEqual(result["functions"]["DIVIDE"]["measure_instances"], 2)
            self.assertEqual(result["functions"]["CALCULATE"]["measure_instances"], 1)
            self.assertEqual(result["patterns"]["time_intelligence"]["measure_instances"], 1)
            self.assertEqual(result["patterns"]["safe_ratio"]["measure_instances"], 2)
            self.assertEqual(result["functions"]["DIVIDE"]["sources"], 2)
            self.assertEqual(result["functions"]["DIVIDE"]["artifact_groups"], 2)
            self.assertEqual(result["corpus"]["artifact_groups"], 3)

            serialized = json.dumps(result)
            self.assertNotIn("Sales Amount Copy", serialized)
            self.assertNotIn("SUMX(Sales", serialized)

    def test_normalization_ignores_spacing_and_comments(self) -> None:
        module = load_module()

        first = module.normalize_dax("SUMX ( Sales, Sales[Qty] * Sales[Price] ) // total")
        second = module.normalize_dax(" sumx(Sales,Sales[Qty]*Sales[Price]) ")

        self.assertEqual(first, second)

    def test_normalization_preserves_string_literal_content(self) -> None:
        module = load_module()

        spaced = module.normalize_dax('IF ( [Flag] = 1, "A, B", "x / y" )')
        compact_outside = module.normalize_dax('if([Flag]=1,"A, B","x / y")')
        changed_comma = module.normalize_dax('IF([Flag]=1,"A,B","x / y")')
        changed_case = module.normalize_dax('IF([Flag]=1,"A, B","X / Y")')

        self.assertEqual(spaced, compact_outside)
        self.assertNotEqual(spaced, changed_comma)
        self.assertNotEqual(spaced, changed_case)

    def test_normalization_preserves_quoted_and_bracketed_identifiers(self) -> None:
        module = load_module()

        spaced_table = module.normalize_dax("SUM ( 'Sales, EU'[Amount] )")
        compact_table = module.normalize_dax("SUM('Sales,EU'[Amount])")
        spaced_measure = module.normalize_dax("SUM ( [Actual, Budget] )")
        compact_measure = module.normalize_dax("SUM([Actual,Budget])")
        comment_like_identifier = module.normalize_dax(
            "SUM('Sales//EU'[Amount]) // actual trailing comment"
        )

        self.assertNotEqual(spaced_table, compact_table)
        self.assertNotEqual(spaced_measure, compact_measure)
        self.assertIn("'Sales//EU'", comment_like_identifier)
        self.assertNotIn("trailing comment", comment_like_identifier)
        self.assertEqual(module.extract_functions("SUM([IF ( Budget )])"), ["SUM"])

    def test_redacts_source_labels_and_unknown_call_tokens_by_default(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            root = Path(tmpdir) / "internal-finance-model"
            root.mkdir()
            (root / "model.bim").write_text(
                json.dumps(
                    {
                        "model": {
                            "tables": [
                                {
                                    "name": "Facts",
                                    "measures": [
                                        {
                                            "name": "Sensitive Measure",
                                            "expression": "SensitiveUdf ( SUM ( Facts[Amount] ) )",
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = module.analyze_paths([root])
            serialized = json.dumps(result)

            self.assertIn("SUM", result["functions"])
            self.assertNotIn("SENSITIVEUDF", serialized.upper())
            self.assertNotIn("internal-finance-model", serialized)
            self.assertEqual(result["redacted_call_tokens"]["unique_tokens"], 1)

    def test_rejects_missing_source_root(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            missing = Path(tmpdir) / "missing"

            with self.assertRaises(FileNotFoundError):
                module.analyze_paths([missing])

    def test_manifest_verification_detects_input_drift(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            root = Path(tmpdir) / "public-source"
            root.mkdir()
            model = root / "model.bim"
            model.write_text('{"model":{"tables":[]}}', encoding="utf-8")
            manifest = {
                "schema_version": "1.0",
                "sources": [
                    {
                        "directory": "public-source",
                        "label": "public-source",
                        "repository": "https://example.test/public-source",
                        "commit": "abc123",
                        "license": "MIT",
                        "content_sha256": module.hash_tree(root),
                    }
                ],
            }

            verified = module.verify_input_manifest([root], manifest)
            self.assertTrue(verified["manifest_verified"])

            model.write_text('{"model":{"tables":[{}]}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                module.verify_input_manifest([root], manifest)

    def test_name_intents_union_across_duplicate_expression_names(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            roots = []
            for folder, measure_name in (("a", "Total Sales"), ("b", "Margin %")):
                root = Path(tmpdir) / folder
                root.mkdir()
                (root / "model.bim").write_text(
                    json.dumps(
                        {
                            "model": {
                                "tables": [
                                    {
                                        "name": "Facts",
                                        "measures": [
                                            {"name": measure_name, "expression": "SUM(Facts[Amount])"}
                                        ],
                                    }
                                ]
                            }
                        }
                    ),
                    encoding="utf-8",
                )
                roots.append(root)

            result = module.analyze_paths(roots)

            self.assertEqual(
                result["name_intent_proxies"]["total_sum"]["unique_expressions"], 1
            )
            self.assertEqual(
                result["name_intent_proxies"]["ratio_percent_margin"]["unique_expressions"],
                1,
            )


if __name__ == "__main__":
    unittest.main()
