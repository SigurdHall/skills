#!/usr/bin/env python3
"""Validate the minimum, non-canonical StoryFrame draft envelope."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT_FIELDS = {"contract", "status", "dataState", "sourceRefs", "frames"}
ROOT_ALLOWED_FIELDS = ROOT_FIELDS | {"canonicalStatus", "knowledgeContext"}
SOURCE_FIELDS = {"storyBrief", "narrativeEvidence", "contentHash"}
SOURCE_OPTIONAL_FIELDS = {"brandIntentRef", "tasteProfileRef"}
SOURCE_ALLOWED_FIELDS = SOURCE_FIELDS | SOURCE_OPTIONAL_FIELDS
KNOWLEDGE_CONTEXT_FIELDS = {
    "selectionId",
    "selectionSha256",
    "registrySnapshotSha256",
    "selectedDomainRefs",
    "unresolvedKnowledgeRequirements",
    "evidenceAdvisories",
}
FRAME_FIELDS = {
    "frameId",
    "order",
    "decisionQuestion",
    "keyClaimRef",
    "evidenceNeeds",
    "comparisonContext",
    "driverStatus",
    "caveats",
    "freshnessRequirement",
    "nextAction",
    "traceRefs",
}
EVIDENCE_FIELDS = {"intent", "priority", "semanticRoleRefs", "factRefs"}
COMPARISON_CONTEXT_FIELDS = {
    "baseline",
    "period",
    "population",
    "scenario",
    "currency",
    "unit",
    "grain",
    "direction",
    "benchmark",
}
FORBIDDEN_TARGET_KEYS = {
    "x",
    "y",
    "width",
    "height",
    "position",
    "left",
    "top",
    "right",
    "bottom",
    "grid",
    "layout",
    "rows",
    "columns",
    "viewport",
    "gridtemplate",
    "gridarea",
    "canvassize",
    "breakpoints",
    "visualtype",
    "charttype",
    "component",
    "componentname",
    "css",
    "dom",
    "dax",
    "sql",
    "physicalfield",
    "tablefield",
}
FORBIDDEN_TARGET_KEY_FRAGMENTS = {
    "pixel",
    "coordinate",
    "grid",
    "css",
    "viewport",
    "breakpoint",
    "visual",
    "component",
    "layout",
    "position",
    "canvas",
}
ALLOWED_STATUSES = {
    "exploratory-pending-evidence",
    "target-request-ready",
    "approved-for-authoring",
    "implemented",
}
ALLOWED_DATA_STATES = {
    "knowledge_only_no_values",
    "synthetic",
    "connected-sampled",
    "connected-live",
}
HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]+$")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _required_fields(value: dict[str, Any], fields: set[str], location: str) -> list[str]:
    return [f"{location}: missing required field '{field}'" for field in sorted(fields - value.keys())]


def _unexpected_fields(value: dict[str, Any], fields: set[str], location: str) -> list[str]:
    return [f"{location}: unexpected field '{field}'" for field in sorted(value.keys() - fields)]


def _is_forbidden_target_key(key: Any) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
    return normalized in FORBIDDEN_TARGET_KEYS or any(
        fragment in normalized for fragment in FORBIDDEN_TARGET_KEY_FRAGMENTS
    )


def _find_forbidden_keys(value: Any, location: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if _is_forbidden_target_key(key):
                errors.append(f"{location}: forbidden target key '{key}'")
            errors.extend(_find_forbidden_keys(nested, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            errors.extend(_find_forbidden_keys(nested, f"{location}[{index}]"))
    return errors


def validate_payload(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root: expected a JSON object"]

    errors.extend(_required_fields(payload, ROOT_FIELDS, "root"))
    errors.extend(_unexpected_fields(payload, ROOT_ALLOWED_FIELDS, "root"))
    contract = payload.get("contract")
    status = payload.get("status")
    data_state = payload.get("dataState")
    if not _is_nonempty_string(contract) or not str(contract).startswith("StoryFrameV1"):
        errors.append("root.contract: expected a StoryFrameV1 draft identifier")
    if not _is_nonempty_string(status):
        errors.append("root.status: expected a non-empty status")
    elif status not in ALLOWED_STATUSES:
        errors.append(f"root.status: unsupported status '{status}'")
    if not _is_nonempty_string(data_state):
        errors.append("root.dataState: expected a non-empty data state")
    elif data_state not in ALLOWED_DATA_STATES:
        errors.append(f"root.dataState: unsupported dataState '{data_state}'")
    pending_evidence = (
        status == "exploratory-pending-evidence"
        or data_state not in {"connected-sampled", "connected-live"}
    )

    knowledge_context = payload.get("knowledgeContext")
    if knowledge_context is not None:
        if not isinstance(knowledge_context, dict):
            errors.append("root.knowledgeContext: expected an object")
        else:
            errors.extend(
                _required_fields(
                    knowledge_context,
                    KNOWLEDGE_CONTEXT_FIELDS,
                    "root.knowledgeContext",
                )
            )
            errors.extend(
                _unexpected_fields(
                    knowledge_context,
                    KNOWLEDGE_CONTEXT_FIELDS,
                    "root.knowledgeContext",
                )
            )
            selection_id = knowledge_context.get("selectionId")
            if not _is_nonempty_string(selection_id) or not ID_PATTERN.fullmatch(
                str(selection_id)
            ):
                errors.append("root.knowledgeContext.selectionId: expected a stable selection ID")
            for field in ("selectionSha256", "registrySnapshotSha256"):
                value = knowledge_context.get(field)
                if not _is_nonempty_string(value) or not HASH_PATTERN.fullmatch(str(value)):
                    errors.append(
                        f"root.knowledgeContext.{field}: expected a lowercase SHA-256 hash"
                    )
            domains = knowledge_context.get("selectedDomainRefs")
            if not isinstance(domains, list) or not all(
                _is_nonempty_string(ref) and str(ref).startswith("domain.") for ref in domains
            ):
                errors.append(
                    "root.knowledgeContext.selectedDomainRefs: expected domain.* string refs"
                )
            elif len(domains) != len(set(domains)):
                errors.append("root.knowledgeContext.selectedDomainRefs: duplicate reference")
            unresolved = knowledge_context.get("unresolvedKnowledgeRequirements")
            if not isinstance(unresolved, list) or not all(
                _is_nonempty_string(item) for item in unresolved
            ):
                errors.append(
                    "root.knowledgeContext.unresolvedKnowledgeRequirements: expected strings"
                )
            advisories = knowledge_context.get("evidenceAdvisories")
            if not isinstance(advisories, list) or not all(
                _is_nonempty_string(item) for item in advisories
            ):
                errors.append("root.knowledgeContext.evidenceAdvisories: expected strings")

    source_refs = payload.get("sourceRefs")
    if not isinstance(source_refs, dict):
        errors.append("root.sourceRefs: expected an object")
        declared_source_refs: dict[str, str] = {}
    else:
        errors.extend(_required_fields(source_refs, SOURCE_FIELDS, "root.sourceRefs"))
        errors.extend(_unexpected_fields(source_refs, SOURCE_ALLOWED_FIELDS, "root.sourceRefs"))
        for field in SOURCE_ALLOWED_FIELDS:
            if field in source_refs and not _is_nonempty_string(source_refs[field]):
                errors.append(f"root.sourceRefs.{field}: expected a non-empty string")
        for field, prefix in (
            ("storyBrief", "brief:"),
            ("narrativeEvidence", "evidence:"),
            ("contentHash", "sha256:"),
            ("brandIntentRef", "brand:"),
            ("tasteProfileRef", "taste:"),
        ):
            value = source_refs.get(field)
            if _is_nonempty_string(value) and not str(value).startswith(prefix):
                errors.append(f"root.sourceRefs.{field}: expected a '{prefix}' reference")
        declared_source_refs = {
            key: str(value)
            for key, value in source_refs.items()
            if key in SOURCE_ALLOWED_FIELDS and _is_nonempty_string(value)
        }

    frames = payload.get("frames")
    if not isinstance(frames, list) or not frames:
        errors.append("root.frames: expected at least one frame")
        frames = []

    frame_ids: set[str] = set()
    frame_orders: set[int] = set()
    for frame_index, frame in enumerate(frames):
        location = f"root.frames[{frame_index}]"
        if not isinstance(frame, dict):
            errors.append(f"{location}: expected an object")
            continue
        errors.extend(_required_fields(frame, FRAME_FIELDS, location))
        errors.extend(_unexpected_fields(frame, FRAME_FIELDS, location))

        frame_id = frame.get("frameId")
        if not _is_nonempty_string(frame_id):
            errors.append(f"{location}.frameId: expected a non-empty string")
        elif frame_id in frame_ids:
            errors.append(f"{location}.frameId: Duplicate frameId '{frame_id}'")
        else:
            frame_ids.add(frame_id)

        order = frame.get("order")
        if not isinstance(order, int) or isinstance(order, bool) or order < 1:
            errors.append(f"{location}.order: expected a positive integer")
        elif order in frame_orders:
            errors.append(f"{location}.order: duplicate order '{order}'")
        else:
            frame_orders.add(order)

        for field in (
            "decisionQuestion",
            "keyClaimRef",
            "driverStatus",
            "freshnessRequirement",
            "nextAction",
        ):
            if field in frame and not _is_nonempty_string(frame[field]):
                errors.append(f"{location}.{field}: expected a non-empty string")

        claim_ref = frame.get("keyClaimRef")
        if _is_nonempty_string(claim_ref) and not str(claim_ref).startswith("claim:"):
            errors.append(f"{location}.keyClaimRef: expected a 'claim:' reference")
        if pending_evidence and _is_nonempty_string(claim_ref) and ":pending" not in str(claim_ref):
            errors.append(f"{location}.keyClaimRef: must be marked pending in no-data status")

        comparison_context = frame.get("comparisonContext")
        if not isinstance(comparison_context, dict):
            errors.append(f"{location}.comparisonContext: expected an object")
        else:
            errors.extend(
                _unexpected_fields(
                    comparison_context,
                    COMPARISON_CONTEXT_FIELDS,
                    f"{location}.comparisonContext",
                )
            )
            for key, value in comparison_context.items():
                if not isinstance(value, (str, int, float, bool, type(None))):
                    errors.append(
                        f"{location}.comparisonContext.{key}: expected a primitive value"
                    )

        caveats = frame.get("caveats")
        if not isinstance(caveats, list) or not all(_is_nonempty_string(item) for item in caveats):
            errors.append(f"{location}.caveats: expected a list of strings")

        trace_refs = frame.get("traceRefs")
        if not isinstance(trace_refs, list) or not trace_refs or not all(
            _is_nonempty_string(ref) for ref in trace_refs
        ):
            errors.append(f"{location}.traceRefs: expected non-empty string refs")
        else:
            if len(trace_refs) != len(set(trace_refs)):
                errors.append(f"{location}.traceRefs: duplicate reference")
            declared_values = set(declared_source_refs.values())
            for ref in trace_refs:
                if ref not in declared_values:
                    errors.append(
                        f"{location}.traceRefs: reference is not declared in root.sourceRefs: '{ref}'"
                    )
            for source_field, source_ref in declared_source_refs.items():
                if source_ref not in trace_refs:
                    errors.append(
                        f"{location}.traceRefs: missing source reference '{source_field}'"
                    )

        evidence_needs = frame.get("evidenceNeeds")
        if not isinstance(evidence_needs, list) or not evidence_needs:
            errors.append(f"{location}.evidenceNeeds: expected at least one evidence need")
            continue
        for evidence_index, evidence in enumerate(evidence_needs):
            evidence_location = f"{location}.evidenceNeeds[{evidence_index}]"
            if not isinstance(evidence, dict):
                errors.append(f"{evidence_location}: expected an object")
                continue
            errors.extend(_required_fields(evidence, EVIDENCE_FIELDS, evidence_location))
            errors.extend(_unexpected_fields(evidence, EVIDENCE_FIELDS, evidence_location))
            for field in ("intent", "priority"):
                if field in evidence and not _is_nonempty_string(evidence[field]):
                    errors.append(f"{evidence_location}.{field}: expected a non-empty string")
            for field, prefix in (("semanticRoleRefs", None), ("factRefs", "fact:")):
                refs = evidence.get(field)
                if not isinstance(refs, list) or not refs or not all(
                    _is_nonempty_string(ref) for ref in refs
                ):
                    errors.append(f"{evidence_location}.{field}: expected non-empty string refs")
                    continue
                if prefix and any(not str(ref).startswith(prefix) for ref in refs):
                    errors.append(f"{evidence_location}.{field}: expected '{prefix}' references")
                if field == "semanticRoleRefs" and any(":" not in str(ref) for ref in refs):
                    errors.append(f"{evidence_location}.{field}: expected typed semantic refs")
                if pending_evidence and field == "factRefs" and any(
                    ":pending" not in str(ref) for ref in refs
                ):
                    errors.append(
                        f"{evidence_location}.{field}: all facts must be marked pending in no-data status"
                    )

    errors.extend(_find_forbidden_keys(payload))
    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("story_frame", type=Path, help="Path to a StoryFrame draft JSON file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = json.loads(args.story_frame.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"Could not read StoryFrame JSON: {exc}\n")
        return 2
    errors = validate_payload(payload)
    if errors:
        sys.stderr.write("\n".join(f"ERROR: {error}" for error in errors) + "\n")
        return 1
    sys.stdout.write("StoryFrame draft is valid.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
