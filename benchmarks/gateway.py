#!/usr/bin/env python3
"""Two-source answer-masked benchmark handoff and conservative metadata grading.

Uses Python stdlib only; does not launch agents, deploy contracts or execute PoCs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
CASE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
GITHUB_RE = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?")
HTTP_TIMEOUT = 20


class GatewayError(Exception):
    pass


def validate_id(case_id: str) -> str:
    if not CASE_RE.fullmatch(case_id):
        raise GatewayError("Invalid case ID: simple identifier required, no paths")
    return case_id


def raw_url(source: str, path: str) -> str:
    conf = SOURCES[source]
    return f"https://raw.githubusercontent.com/{conf['repository']}/{conf['ref']}/{path}"


def fetch_text(source: str, path: str) -> str:
    request = urllib.request.Request(
        raw_url(source, path),
        headers={"User-Agent": "SFS-Security-Benchmark-Gateway/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            data = response.read(2_000_001)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise GatewayError(f"Upstream file unavailable: {path} ({exc})") from exc
    if len(data) > 2_000_000:
        raise GatewayError("Upstream input too large")
    return data.decode("utf-8")


def yaml_scalar(contents: str, key: str) -> str | None:
    match = re.search(
        rf"(?m)^{re.escape(key)}:\s*['\"]?([^\n#'\"]+)", contents
    )
    return match.group(1).strip() if match else None


def case_alias(source: str, case_id: str) -> str:
    return "audit-" + hashlib.sha256(
        f"{source}:{case_id}".encode()
    ).hexdigest()[:12]


def load_reference(source: str, case_id: str) -> dict:
    validate_id(case_id)
    if source == "cyberchainbench":
        document = json.loads(fetch_text(
            source, f"data/benchmark/cases/{case_id}.json"
        ))
        if document.get("id") != case_id:
            raise GatewayError("Case ID mismatch")
        for field in ("chain", "vulnerable_address", "block_number", "type", "function"):
            if field not in document:
                raise GatewayError(f"Case missing required field: {field}")
        if not re.fullmatch(r"0x[a-fA-F0-9]{40}", str(document["vulnerable_address"])):
            raise GatewayError("Invalid contract address")
        return document

    if source == "reevmbench":
        config = fetch_text(source, f"audits/{case_id}/config.yaml")
        dockerfile = fetch_text(source, f"audits/{case_id}/Dockerfile")
        repository = GITHUB_RE.search(dockerfile)
        commit = yaml_scalar(config, "base_commit")
        if yaml_scalar(config, "id") != case_id:
            raise GatewayError("Case ID mismatch")
        if not repository or not commit or not re.fullmatch(r"[a-fA-F0-9]{40}", commit):
            raise GatewayError("Pinned target source unavailable in this audit")
        vuln_ids = re.findall(
            r'(?m)^\s+- id:\s*["\']?([A-Za-z0-9_-]+)', config
        )
        return {
            "id": case_id,
            "repo_url": repository.group(0).removesuffix(".git"),
            "base_commit": commit,
            "run_cmd_dir": yaml_scalar(config, "run_cmd_dir"),
            "vulnerability_ids": vuln_ids,
        }
    raise GatewayError("Unsupported source")


def prepare(source: str, case_id: str, phase: str) -> dict:
    document = load_reference(source, case_id)
    brief = {
        "schema": "sfs-benchmark-brief-v1",
        "task": "independent-security-audit" if phase == "detect" else "historical-reproduction",
        "alias": case_alias(source, case_id),
        "instructions": (
            "Use ctf-skill-index V7 and all available security tools. Independently "
            "derive findings from the authorized historical target. Freeze the "
            "report and evidence before evaluator access. Do not inspect upstream "
            "benchmark ground truth, patches or incident reports."
        ),
        "submission_schema": {
            "findings": [{
                "type": "string or null",
                "function": "string or null",
                "finding_id": "string or null",
                "evidence_path": "string or null",
            }],
            "notes": "string",
        },
        "provenance": {
            "benchmark": source,
            "ref": SOURCES[source]["ref"],
        },
    }
    if source == "cyberchainbench":
        brief["target"] = {
            "chain": document["chain"],
            "contract_address": document["vulnerable_address"],
        }
        if phase == "reproduce":
            brief["target"]["historical_block"] = document["block_number"]
    else:
        brief["target"] = {
            "source_repository": document["repo_url"],
            "source_commit": document["base_commit"],
            "working_subdirectory": document.get("run_cmd_dir"),
        }
    # No case IDs, incident names, known attack txs, fix text, vuln labels or functions.
    return brief


def grade(source: str, case_id: str, submission: dict) -> dict:
    document = load_reference(source, case_id)
    findings = submission.get("findings", [])
    if not isinstance(findings, list) or len(findings) > 100 or not all(
        isinstance(f, dict) for f in findings
    ):
        raise GatewayError("Submission requires findings: array of <=100 objects")
    grade_result = {
        "schema": "sfs-benchmark-grade-v1",
        "alias": case_alias(source, case_id),
        "benchmark": source,
        "reported_findings": len(findings),
        "independent_reproduction": "NOT_VERIFIED",
        "warning": "Metadata matching alone does not establish exploitability or soundness.",
    }
    if source == "cyberchainbench":
        expected_type = str(document["type"]).casefold().strip()
        expected_function = str(document["function"]).casefold().strip()
        matches = [
            i for i, finding in enumerate(findings)
            if str(finding.get("type") or "").casefold().strip() == expected_type
            and str(finding.get("function") or "").casefold().strip() == expected_function
        ]
        grade_result["label_match"] = bool(matches)
        grade_result["matching_finding_indices"] = matches
        grade_result["status"] = (
            "LABEL_MATCH_UNVERIFIED" if matches else "NO_EXACT_LABEL_MATCH"
        )
    else:
        gold_ids = set(document["vulnerability_ids"])
        matches = [
            i for i, finding in enumerate(findings)
            if finding.get("finding_id") in gold_ids
        ]
        grade_result["finding_id_match"] = bool(matches)
        grade_result["matching_finding_indices"] = matches
        grade_result["status"] = (
            "ID_MATCH_UNVERIFIED" if matches else "MANUAL_REVIEW_REQUIRED"
        )
        grade_result["warning"] = (
            "ReEVMBench finding IDs alone cannot validate a technical finding; "
            "review code and exploit evidence independently."
        )
    return grade_result


def confined_submission_path(argument: str) -> Path:
    root = (HERE / "submissions").resolve()
    target = (root / argument).resolve()
    if not target.is_relative_to(root) or target.suffix != ".json" or not target.is_file():
        raise GatewayError("Submission must be an existing JSON under benchmarks/submissions/")
    if target.stat().st_size > 1_000_000:
        raise GatewayError("Submission too large")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "grade"])
    parser.add_argument("--source", choices=sorted(SOURCES), required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--phase", choices=["detect", "reproduce"], default="detect")
    parser.add_argument("--submission", help="JSON filename inside benchmarks/submissions/")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args(argv)

    try:
        validate_id(args.case_id)
        if args.command == "prepare":
            result = prepare(args.source, args.case_id, args.phase)
        else:
            if not args.submission:
                raise GatewayError("--submission required for grade")
            result = grade(
                args.source, args.case_id,
                json.loads(confined_submission_path(args.submission).read_text(encoding="utf-8")),
            )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"{args.command}: {args.source} / {args.case_id} -> {output}")
        return 0
    except (GatewayError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"Gateway error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
