#!/usr/bin/env python3
"""Aggregate DAX measure patterns without exporting names or expressions."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, NamedTuple


class MeasureRecord(NamedTuple):
    name: str
    expression: str
    source: str
    model: str
    path: Path


DECLARATION_RE = re.compile(
    r"^(?P<indent>\s*)(?P<kind>measure|calculationItem|column|table)\s+"
    r"(?P<name>'(?:''|[^'])*'|[^=]+?)\s*=\s*(?P<rhs>.*)$",
    re.IGNORECASE,
)
TMDL_METADATA_RE = re.compile(
    r"^(?:formatString|formatStringDefinition|description|displayFolder|lineageTag|"
    r"dataCategory|isHidden|annotation|extendedProperty|changedProperty|summarizeBy|"
    r"sourceColumn|dataType|sortByColumn|isNameInferred|isDataTypeInferred)\b",
    re.IGNORECASE,
)
FUNCTION_RE = re.compile(r"\b([A-Z][A-Z0-9_.]*)\s*\(")
PARTITION_CALCULATED_RE = re.compile(r"^\s*partition\s+.+?=\s*calculated\b", re.IGNORECASE)
UDF_RE = re.compile(r"^\s*function\s+", re.IGNORECASE)


PATTERN_FUNCTIONS: dict[str, set[str]] = {
    "base_aggregation": {
        "SUM",
        "SUMX",
        "COUNT",
        "COUNTA",
        "COUNTAX",
        "COUNTROWS",
        "DISTINCTCOUNT",
        "AVERAGE",
        "AVERAGEX",
        "MIN",
        "MINX",
        "MAX",
        "MAXX",
    },
    "context_filtering": {
        "CALCULATE",
        "CALCULATETABLE",
        "FILTER",
        "ALL",
        "ALLSELECTED",
        "ALLEXCEPT",
        "REMOVEFILTERS",
        "KEEPFILTERS",
    },
    "time_intelligence": {
        "DATEADD",
        "DATESYTD",
        "DATESQTD",
        "DATESMTD",
        "TOTALYTD",
        "TOTALQTD",
        "TOTALMTD",
        "SAMEPERIODLASTYEAR",
        "PREVIOUSYEAR",
        "PREVIOUSQUARTER",
        "PREVIOUSMONTH",
        "PARALLELPERIOD",
        "DATESINPERIOD",
        "DATESBETWEEN",
        "STARTOFYEAR",
        "STARTOFQUARTER",
        "STARTOFMONTH",
        "ENDOFYEAR",
        "ENDOFQUARTER",
        "ENDOFMONTH",
    },
    "iterator": {
        "SUMX",
        "AVERAGEX",
        "COUNTX",
        "COUNTAX",
        "MINX",
        "MAXX",
        "RANKX",
        "CONCATENATEX",
        "PRODUCTX",
    },
    "safe_ratio": {"DIVIDE"},
    "conditional_logic": {"IF", "IFS", "SWITCH", "IFERROR"},
    "selection_state": {
        "SELECTEDVALUE",
        "HASONEVALUE",
        "ISINSCOPE",
        "SELECTEDMEASURE",
        "SELECTEDMEASURENAME",
        "ISSELECTEDMEASURE",
    },
    "blank_error_handling": {"BLANK", "ISBLANK", "COALESCE", "IFERROR"},
    "virtual_relationship": {"TREATAS", "USERELATIONSHIP", "CROSSFILTER"},
    "table_shaping": {"SUMMARIZE", "SUMMARIZECOLUMNS", "ADDCOLUMNS", "SELECTCOLUMNS", "GROUPBY"},
    "ranking_topn": {"RANKX", "TOPN"},
    "text_display": {"FORMAT", "CONCATENATE", "CONCATENATEX", "UNICHAR"},
}

NAME_PATTERNS: dict[str, re.Pattern[str]] = {
    "total_sum": re.compile(r"\b(total|sum)\b", re.IGNORECASE),
    "count_number": re.compile(r"\b(count|number|#)\b", re.IGNORECASE),
    "ratio_percent_margin": re.compile(r"(%|\b(percent|percentage|ratio|share|margin|rate)\b)", re.IGNORECASE),
    "variance_change_growth": re.compile(r"(Δ|\b(variance|var|change|growth|delta|difference)\b)", re.IGNORECASE),
    "ytd_mtd_qtd": re.compile(r"\b(ytd|mtd|qtd|year to date|month to date|quarter to date)\b", re.IGNORECASE),
    "previous_period": re.compile(r"\b(previous|prior|last year|ly|py|lm|pq)\b", re.IGNORECASE),
    "target_budget_forecast": re.compile(r"\b(target|budget|forecast|plan|goal|scenario)\b", re.IGNORECASE),
    "average": re.compile(r"\b(average|avg|mean)\b", re.IGNORECASE),
    "rank_topn": re.compile(r"\b(rank|ranking|top|bottom)\b", re.IGNORECASE),
    "quality_exception": re.compile(r"\b(quality|exception|error|invalid|status|freshness)\b", re.IGNORECASE),
}

SAFE_DAX_FUNCTIONS = set().union(*PATTERN_FUNCTIONS.values()) | {
    "ABS",
    "AND",
    "AVERAGE",
    "COUNT",
    "COUNTA",
    "CURRENCY",
    "DATE",
    "DATEDIFF",
    "DATEVALUE",
    "DAY",
    "DISTINCT",
    "FIRSTDATE",
    "FIRSTNONBLANK",
    "GENERATEALL",
    "IF.EAGER",
    "INT",
    "LASTDATE",
    "LOWER",
    "MOD",
    "MONTH",
    "MROUND",
    "OFFSET",
    "ORDERBY",
    "PERCENTILE.INC",
    "PERCENTILEX.INC",
    "POWER",
    "QUARTER",
    "RAND",
    "RELATED",
    "RELATEDTABLE",
    "ROUND",
    "TODAY",
    "TRUE",
    "UPPER",
    "VALUE",
    "VALUES",
    "YEAR",
}


def _expression_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(str(part) for part in value)
    return ""


def _consume_protected(expression: str, index: int) -> tuple[str, int]:
    opener = expression[index]
    closer = "]" if opener == "[" else opener
    output = [opener]
    index += 1
    while index < len(expression):
        char = expression[index]
        output.append(char)
        if char == closer:
            if index + 1 < len(expression) and expression[index + 1] == closer:
                output.append(closer)
                index += 2
                continue
            return "".join(output), index + 1
        index += 1
    return "".join(output), index


def strip_dax_comments(expression: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(expression):
        char = expression[index]
        next_char = expression[index + 1] if index + 1 < len(expression) else ""
        if char in {'"', "'", "["}:
            protected, index = _consume_protected(expression, index)
            output.append(protected)
            continue
        if char == "/" and next_char == "/":
            index += 2
            while index < len(expression) and expression[index] not in "\r\n":
                index += 1
            continue
        if char == "/" and next_char == "*":
            index += 2
            while index + 1 < len(expression) and expression[index : index + 2] != "*/":
                index += 1
            index = min(index + 2, len(expression))
            continue
        output.append(char)
        index += 1
    return "".join(output)


def _iter_dax_segments(expression: str) -> Iterable[tuple[str, str]]:
    normal: list[str] = []
    index = 0
    kinds = {'"': "string", "'": "quoted_identifier", "[": "bracket_identifier"}
    while index < len(expression):
        char = expression[index]
        kind = kinds.get(char)
        if kind is None:
            normal.append(char)
            index += 1
            continue
        if normal:
            yield "normal", "".join(normal)
            normal.clear()
        protected, index = _consume_protected(expression, index)
        yield kind, protected
    if normal:
        yield "normal", "".join(normal)


def _transform_unprotected(expression: str, transform) -> str:
    return "".join(
        transform(segment) if kind == "normal" else segment
        for kind, segment in _iter_dax_segments(expression)
    )


def _uppercase_outside_strings(expression: str) -> str:
    return _transform_unprotected(expression, str.upper)


def _normalize_spacing_outside_strings(expression: str) -> str:
    def normalize_segment(segment: str) -> str:
        segment = re.sub(r"\s+", " ", segment)
        segment = re.sub(r"\s*([(),+*/=<>])\s*", r"\1", segment)
        return re.sub(r"\s+-\s+", "-", segment)

    return _transform_unprotected(expression, normalize_segment).strip()


def normalize_dax(expression: str) -> str:
    normalized = unicodedata.normalize("NFC", expression.lstrip("\ufeff"))
    normalized = strip_dax_comments(normalized).replace("\r\n", "\n").replace("\r", "\n")
    normalized = _uppercase_outside_strings(normalized)
    return _normalize_spacing_outside_strings(normalized)


def _without_strings(expression: str) -> str:
    return "".join(
        segment if kind == "normal" else " " * len(segment)
        for kind, segment in _iter_dax_segments(expression)
    )


def extract_call_tokens(expression: str) -> list[str]:
    text = _uppercase_outside_strings(_without_strings(strip_dax_comments(expression)))
    return FUNCTION_RE.findall(text)


def extract_functions(expression: str) -> list[str]:
    return [token for token in extract_call_tokens(expression) if token in SAFE_DAX_FUNCTIONS]


def _unquote_name(name: str) -> str:
    name = name.strip()
    if name.startswith("'") and name.endswith("'"):
        return name[1:-1].replace("''", "'")
    return name


def _indent_width(text: str) -> int:
    return len(text.expandtabs(4))


def _parse_tmdl_declarations(path: Path, source: str, model: str) -> tuple[list[MeasureRecord], Counter[str]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    records: list[MeasureRecord] = []
    excluded: Counter[str] = Counter()
    index = 0
    while index < len(lines):
        line = lines[index]
        if PARTITION_CALCULATED_RE.match(line):
            excluded["calculated_tables"] += 1
        if UDF_RE.match(line):
            excluded["udf_definitions"] += 1
        match = DECLARATION_RE.match(line)
        if not match:
            index += 1
            continue

        kind = match.group("kind").lower()
        name = _unquote_name(match.group("name"))
        rhs = match.group("rhs").strip()
        base_indent = _indent_width(match.group("indent"))
        expression_lines: list[str] = []
        next_index = index + 1

        if rhs.startswith("```"):
            remainder = rhs[3:].strip()
            if remainder and remainder != "```":
                expression_lines.append(remainder.removesuffix("```").rstrip())
            if not rhs.endswith("```") or rhs == "```":
                while next_index < len(lines):
                    candidate = lines[next_index]
                    if candidate.strip() == "```":
                        next_index += 1
                        break
                    expression_lines.append(candidate.strip())
                    next_index += 1
        else:
            if rhs:
                expression_lines.append(rhs)
            while next_index < len(lines):
                candidate = lines[next_index]
                stripped = candidate.strip()
                if not stripped:
                    if expression_lines:
                        expression_lines.append("")
                    next_index += 1
                    continue
                candidate_indent = _indent_width(candidate) - _indent_width(candidate.lstrip())
                if candidate_indent <= base_indent:
                    break
                if TMDL_METADATA_RE.match(stripped):
                    break
                if DECLARATION_RE.match(candidate) or PARTITION_CALCULATED_RE.match(candidate):
                    break
                expression_lines.append(stripped)
                next_index += 1

        expression = "\n".join(expression_lines).strip()
        if kind == "measure" and expression:
            records.append(MeasureRecord(name, expression, source, model, path))
        elif kind == "calculationitem":
            excluded["calculation_items"] += 1
        elif kind == "column":
            excluded["calculated_columns"] += 1
        elif kind == "table":
            excluded["calculated_tables"] += 1
        index = max(next_index, index + 1)
    return records, excluded


def _iter_table_nodes(node: Any) -> Iterable[dict[str, Any]]:
    if isinstance(node, dict):
        tables = node.get("tables")
        if isinstance(tables, list):
            for table in tables:
                if isinstance(table, dict):
                    yield table
        for key, value in node.items():
            if key != "tables":
                yield from _iter_table_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_table_nodes(value)


def _parse_bim(path: Path, source: str, model: str) -> tuple[list[MeasureRecord], Counter[str]]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    records: list[MeasureRecord] = []
    excluded: Counter[str] = Counter()
    for table in _iter_table_nodes(payload):
        table_name = str(table.get("name", ""))
        for measure in table.get("measures", []) or []:
            if not isinstance(measure, dict):
                continue
            expression = _expression_text(measure.get("expression"))
            if expression:
                records.append(
                    MeasureRecord(str(measure.get("name", "")), expression, source, model, path)
                )
        for column in table.get("columns", []) or []:
            if isinstance(column, dict) and _expression_text(column.get("expression")):
                excluded["calculated_columns"] += 1
        calculation_group = table.get("calculationGroup")
        if isinstance(calculation_group, dict):
            excluded["calculation_items"] += len(calculation_group.get("calculationItems", []) or [])
        partitions = table.get("partitions", []) or []
        if any(
            isinstance(partition, dict)
            and isinstance(partition.get("source"), dict)
            and str(partition["source"].get("type", "")).lower() == "calculated"
            for partition in partitions
        ):
            excluded["calculated_tables"] += 1
        if not table_name:
            continue
    return records, excluded


def _model_id(path: Path, source_root: Path) -> str:
    relative = path.relative_to(source_root)
    for parent in path.parents:
        if parent == source_root.parent:
            break
        if parent.name.endswith(".SemanticModel"):
            return parent.name
    parts = list(relative.parts)
    if "definition" in parts:
        marker = parts.index("definition")
        return "/".join(parts[:marker]) or source_root.name
    if "tables" in parts:
        marker = parts.index("tables")
        return "/".join(parts[:marker]) or source_root.name
    return str(relative.with_suffix(""))


def _parse_measure_json(path: Path, source: str, model: str) -> MeasureRecord | None:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        return None
    expression = _expression_text(payload.get("expression"))
    if not expression:
        return None
    return MeasureRecord(str(payload.get("name") or path.stem), expression, source, model, path)


def hash_tree(root: Path) -> str:
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Corpus source root not found: {root}")
    digest = hashlib.sha256()
    for path in sorted(
        (item for item in root.rglob("*") if item.is_file() and ".git" not in item.parts),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def verify_input_manifest(paths: list[Path], manifest: dict[str, Any]) -> dict[str, Any]:
    entries = manifest.get("sources")
    if not isinstance(entries, list) or len(entries) != len(paths):
        raise ValueError("Manifest must contain exactly one source entry per input root")
    required = {
        "directory",
        "label",
        "repository",
        "commit",
        "license",
        "content_sha256",
    }
    by_directory: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not required.issubset(entry):
            raise ValueError(f"Manifest source {index} is missing required provenance fields")
        directory = str(entry["directory"])
        if directory in by_directory:
            raise ValueError(f"Duplicate manifest directory: {directory}")
        by_directory[directory] = entry

    source_labels: dict[str, str] = {}
    revisions: list[dict[str, str]] = []
    for path in paths:
        resolved = path.resolve()
        if not resolved.is_dir():
            raise FileNotFoundError(f"Corpus source root not found: {resolved}")
        entry = by_directory.get(resolved.name)
        if entry is None:
            raise ValueError(f"No manifest entry for input directory: {resolved.name}")
        actual_hash = hash_tree(resolved)
        expected_hash = str(entry["content_sha256"]).lower()
        if actual_hash != expected_hash:
            raise ValueError(
                f"Input drift for {resolved.name}: expected {expected_hash}, got {actual_hash}"
            )
        source_labels[resolved.name] = str(entry["label"])
        revisions.append(
            {
                "label": str(entry["label"]),
                "repository": str(entry["repository"]),
                "commit": str(entry["commit"]),
                "license": str(entry["license"]),
                "content_sha256": actual_hash,
            }
        )

    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "manifest_verified": True,
        "manifest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "source_labels": source_labels,
        "source_revisions": revisions,
    }


def _collect_from_root(
    root: Path, source_label: str = "source-redacted"
) -> tuple[list[MeasureRecord], Counter[str], int, int]:
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Corpus source root not found: {root}")
    source = source_label
    records: list[MeasureRecord] = []
    excluded: Counter[str] = Counter()
    files_scanned = 0
    parse_errors = 0
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=str):
        suffix = path.suffix.lower()
        if suffix not in {".bim", ".tmdl", ".json", ".dax"}:
            continue
        lower_parts = [part.lower() for part in path.parts]
        relevant_json = suffix == ".json" and (
            "measures" in lower_parts or "calculationitems" in lower_parts
        )
        relevant_dax = suffix == ".dax" and any(
            segment in lower_parts for segment in ("measures", "columns")
        )
        relevant_dax = relevant_dax or (
            suffix == ".dax"
            and (
                "measure" in path.stem.lower()
                or path.name.lower() == "table.dax"
                or "table--calculated" in path.stem.lower()
            )
        )
        if suffix in {".json", ".dax"} and not (relevant_json or relevant_dax):
            continue
        files_scanned += 1
        model = _model_id(path, root)
        try:
            if suffix == ".bim":
                parsed, counts = _parse_bim(path, source, model)
                records.extend(parsed)
                excluded.update(counts)
            elif suffix == ".tmdl":
                parsed, counts = _parse_tmdl_declarations(path, source, model)
                records.extend(parsed)
                excluded.update(counts)
            elif "calculationitems" in lower_parts:
                excluded["calculation_items"] += 1
            elif "columns" in lower_parts and suffix == ".dax":
                excluded["calculated_columns"] += 1
            elif path.name.lower() == "table.dax" or "table--calculated" in path.stem.lower():
                excluded["calculated_tables"] += 1
            elif "measures" in lower_parts or "measure" in path.stem.lower():
                json_sibling = path.with_suffix(".json")
                if suffix == ".dax" and json_sibling.exists():
                    continue
                if suffix == ".json":
                    record = _parse_measure_json(path, source, model)
                    if record:
                        records.append(record)
                else:
                    expression = path.read_text(encoding="utf-8-sig").strip()
                    if expression:
                        records.append(MeasureRecord(path.stem, expression, source, model, path))
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            parse_errors += 1
    return records, excluded, files_scanned, parse_errors


def _percentile(values: list[int], percentile: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(round((len(ordered) - 1) * percentile), len(ordered) - 1)
    return ordered[index]


def _counter_stats(
    records: list[MeasureRecord],
    unique_records: list[MeasureRecord],
    extractor,
) -> dict[str, dict[str, Any]]:
    instance_presence: Counter[str] = Counter()
    unique_presence: Counter[str] = Counter()
    calls: Counter[str] = Counter()
    artifact_groups: defaultdict[str, set[str]] = defaultdict(set)
    sources: defaultdict[str, set[str]] = defaultdict(set)
    for record in records:
        values = list(extractor(record))
        instance_presence.update(set(values))
        calls.update(values)
        for value in set(values):
            artifact_groups[value].add(f"{record.source}::{record.model}")
            sources[value].add(record.source)
    for record in unique_records:
        unique_presence.update(set(extractor(record)))
    result: dict[str, dict[str, Any]] = {}
    for key in sorted(instance_presence, key=lambda item: (-unique_presence[item], item)):
        result[key] = {
            "measure_instances": instance_presence[key],
            "unique_expressions": unique_presence[key],
            "artifact_groups": len(artifact_groups[key]),
            "sources": len(sources[key]),
            "calls": calls[key],
        }
    return result


def _pattern_names(record: MeasureRecord) -> list[str]:
    functions = set(extract_functions(record.expression))
    patterns = [
        name for name, required in PATTERN_FUNCTIONS.items() if functions.intersection(required)
    ]
    if re.search(r"\bVAR\b", _uppercase_outside_strings(_without_strings(record.expression))):
        patterns.append("var_based")
    if not functions and re.fullmatch(r"\s*\[[^\]]+\]\s*", record.expression):
        patterns.append("reference_only")
    return patterns


def _name_intents(record: MeasureRecord) -> list[str]:
    return [name for name, pattern in NAME_PATTERNS.items() if pattern.search(record.name)]


def _name_intent_stats(records: list[MeasureRecord]) -> dict[str, dict[str, Any]]:
    instance_presence: Counter[str] = Counter()
    calls: Counter[str] = Counter()
    expression_hashes: defaultdict[str, set[str]] = defaultdict(set)
    artifact_groups: defaultdict[str, set[str]] = defaultdict(set)
    sources: defaultdict[str, set[str]] = defaultdict(set)
    for record in records:
        values = _name_intents(record)
        instance_presence.update(set(values))
        calls.update(values)
        digest = hashlib.sha256(normalize_dax(record.expression).encode("utf-8")).hexdigest()
        for value in set(values):
            expression_hashes[value].add(digest)
            artifact_groups[value].add(f"{record.source}::{record.model}")
            sources[value].add(record.source)
    return {
        key: {
            "measure_instances": instance_presence[key],
            "unique_expressions": len(expression_hashes[key]),
            "artifact_groups": len(artifact_groups[key]),
            "sources": len(sources[key]),
            "calls": calls[key],
        }
        for key in sorted(instance_presence, key=lambda item: (-len(expression_hashes[item]), item))
    }


def analyze_paths(
    paths: list[Path],
    *,
    source_labels: dict[Path, str] | None = None,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    records: list[MeasureRecord] = []
    excluded: Counter[str] = Counter()
    files_scanned = 0
    parse_errors = 0
    resolved_paths = [path.resolve() for path in paths]
    for index, path in enumerate(resolved_paths, start=1):
        if not path.is_dir():
            raise FileNotFoundError(f"Corpus source root not found: {path}")
        label = (
            source_labels.get(path, f"source-{index:02d}")
            if source_labels is not None
            else f"source-{index:02d}"
        )
        parsed, counts, scanned, errors = _collect_from_root(path, label)
        records.extend(parsed)
        excluded.update(counts)
        files_scanned += scanned
        parse_errors += errors

    by_hash: dict[str, MeasureRecord] = {}
    hash_counts: Counter[str] = Counter()
    for record in records:
        digest = hashlib.sha256(normalize_dax(record.expression).encode("utf-8")).hexdigest()
        hash_counts[digest] += 1
        by_hash.setdefault(digest, record)
    unique_records = list(by_hash.values())

    unknown_tokens: set[str] = set()
    unknown_occurrences = 0
    expressions_with_unknown_tokens: set[str] = set()
    for record in records:
        tokens = [
            token for token in extract_call_tokens(record.expression) if token not in SAFE_DAX_FUNCTIONS
        ]
        if not tokens:
            continue
        unknown_tokens.update(tokens)
        unknown_occurrences += len(tokens)
        expressions_with_unknown_tokens.add(
            hashlib.sha256(normalize_dax(record.expression).encode("utf-8")).hexdigest()
        )

    function_stats = _counter_stats(records, unique_records, lambda record: extract_functions(record.expression))
    pattern_stats = _counter_stats(records, unique_records, _pattern_names)
    name_stats = _name_intent_stats(records)

    pairs: Counter[tuple[str, str]] = Counter()
    for record in unique_records:
        functions = sorted(set(extract_functions(record.expression)))
        for left_index, left in enumerate(functions):
            for right in functions[left_index + 1 :]:
                pairs[(left, right)] += 1

    source_stats: dict[str, dict[str, int]] = {}
    for source in sorted({record.source for record in records}):
        source_records = [record for record in records if record.source == source]
        source_stats[source] = {
            "measure_instances": len(source_records),
            "unique_expressions": len(
                {normalize_dax(record.expression) for record in source_records}
            ),
            "artifact_groups": len({record.model for record in source_records}),
        }

    lengths = [len(record.expression) for record in unique_records]
    lines = [max(1, len(record.expression.splitlines())) for record in unique_records]
    function_counts = [len(extract_call_tokens(record.expression)) for record in unique_records]
    duplicate_histogram = Counter(hash_counts.values())
    provenance_output = {
        "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "manifest_verified": bool(provenance and provenance.get("manifest_verified")),
        "manifest_sha256": provenance.get("manifest_sha256") if provenance else None,
        "source_revisions": provenance.get("source_revisions", []) if provenance else [],
    }
    return {
        "schema_version": "1.1",
        "provenance": provenance_output,
        "corpus": {
            "sources": len(paths),
            "artifact_groups": len(
                {f"{record.source}::{record.model}" for record in records}
            ),
            "recognized_candidate_files": files_scanned,
            "measure_instances": len(records),
            "unique_expressions": len(unique_records),
            "duplicate_instances": len(records) - len(unique_records),
            "calculation_items_excluded": excluded["calculation_items"],
            "calculated_columns_excluded": excluded["calculated_columns"],
            "calculated_tables_excluded": excluded["calculated_tables"],
            "udf_definitions_excluded": excluded["udf_definitions"],
            "read_parse_errors": parse_errors,
            "parser_scope": "recognized BIM, TMDL, and pbi-tools/standalone measure candidates; not a full DAX grammar validator",
        },
        "sources": source_stats,
        "functions": function_stats,
        "redacted_call_tokens": {
            "unique_tokens": len(unknown_tokens),
            "occurrences": unknown_occurrences,
            "unique_expressions": len(expressions_with_unknown_tokens),
        },
        "patterns": pattern_stats,
        "name_intent_proxies": name_stats,
        "function_co_occurrence": [
            {"functions": [left, right], "unique_expressions": count}
            for (left, right), count in sorted(pairs.items(), key=lambda item: (-item[1], item[0]))[:50]
        ],
        "complexity": {
            "median_characters": round(statistics.median(lengths)) if lengths else 0,
            "p90_characters": _percentile(lengths, 0.9),
            "median_lines": round(statistics.median(lines)) if lines else 0,
            "p90_lines": _percentile(lines, 0.9),
            "median_function_calls": round(statistics.median(function_counts)) if function_counts else 0,
            "p90_function_calls": _percentile(function_counts, 0.9),
        },
        "duplicate_frequency": {
            str(frequency): expression_count
            for frequency, expression_count in sorted(duplicate_histogram.items())
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Corpus source roots")
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Verify roots against a pinned public-source manifest and expose its safe labels",
    )
    parser.add_argument("--output", type=Path, help="Write aggregate JSON to this file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    provenance: dict[str, Any] | None = None
    labels: dict[Path, str] | None = None
    if args.manifest:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        provenance = verify_input_manifest(args.paths, manifest)
        labels = {
            path.resolve(): provenance["source_labels"][path.resolve().name]
            for path in args.paths
        }
    result = analyze_paths(args.paths, source_labels=labels, provenance=provenance)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(payload)
    return 0 if result["corpus"]["read_parse_errors"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
