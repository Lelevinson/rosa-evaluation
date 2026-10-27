"""Refresh documentation from saved public checkpoints; never run experiments."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "PROJECT_MASTER_README.md"
LIVE = ROOT / "artifacts/macro-m4-20261027"
START = "<!-- PROJECT_STATUS_START -->"
END = "<!-- PROJECT_STATUS_END -->"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}


def audit_pass(row):
    return (row.get("local_audit", {}).get("pass") is True
            and row.get("phoenix_audit", {}).get("pass") is True)


def backend_status(backend, reviews):
    checkpoint = read_json(LIVE / backend / "checkpoint.json")
    rows = checkpoint.get("trials", [])
    review_counts = {"passed": 0, "failed": 0, "pending_or_invalid": 0}
    for row in rows:
        if row.get("case") != "ambiguous_goal":
            continue
        key = backend + "/" + row["job"]["id"]
        review = reviews.get(key, {})
        digest = hashlib.sha256(json.dumps(row["answer"], sort_keys=True).encode()).hexdigest()
        if (review.get("answer_sha256") != digest
                or type(review.get("pass")) is not bool or not review.get("reason")):
            review_counts["pending_or_invalid"] += 1
        else:
            review_counts["passed" if review["pass"] else "failed"] += 1
    conditions = {}
    for condition in ("primitives", "macro"):
        subset = [row for row in rows if row.get("condition") == condition]
        conditions[condition] = {
            "recorded_rows": len(subset),
            "audited_rows": sum(audit_pass(row) for row in subset),
            # Clarification adjudication remains separate; this is not a final verdict.
            "audited_automatic_primary_passes": sum(
                audit_pass(row) and row.get("primary_pass") is True for row in subset),
            "recorded_model_requests": sum(row["inference"]["calls"] for row in subset),
            "recorded_native_operations": sum(row["score"]["native_operations"] for row in subset),
        }
    clean = (checkpoint.get("simulator_cleanup", {}).get("returncode") == 0
             and checkpoint.get("cleanup_errors") == [])
    return {
        "status": checkpoint.get("status", "UNSTARTED"),
        "scheduled": 40,
        "recorded_rows": len(rows),
        "audited_rows": sum(audit_pass(row) for row in rows),
        "current_trial": checkpoint.get("current_trial"),
        "reserved_requests": checkpoint.get("campaign", {}).get("reserved_requests"),
        "request_cap": checkpoint.get("campaign", {}).get("request_cap"),
        "conditions": conditions,
        "clarification_review": review_counts,
        "required_clarification_reviews": 4,
        "execution_and_audits_complete": (
            checkpoint.get("status") == "COMPLETE" and len(rows) == 40
            and all(audit_pass(row) for row in rows) and clean),
        "simulator_cleanup": checkpoint.get("simulator_cleanup"),
        "checkpoint_sha256": hashlib.sha256(
            json.dumps(checkpoint, sort_keys=True).encode()).hexdigest(),
    }


def snapshot():
    reviews = read_json(LIVE / "clarification-review.json")
    freeze = read_json(LIVE / "freeze.json")
    mismatches = []
    for name, expected in freeze.get("files", {}).items():
        path = ROOT.parent / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            mismatches.append(name)
    return {
        "snapshot_date": datetime.now(ZoneInfo("Asia/Taipei")).date().isoformat(),
        "scope": "Saved checkpoint snapshot, not a live process probe or final research verdict",
        "operator_phase": read_json(LIVE / "operator/status.json").get("phase", "unavailable"),
        "frozen_files": len(freeze.get("files", {})),
        "freeze_mismatches": mismatches,
        "backends": {backend: backend_status(backend, reviews) for backend in ("siwc", "ollama")},
    }


def render(data):
    lines = [f"Saved-checkpoint snapshot: **{data['snapshot_date']}**.", "",
             "| Backend | Saved status | Recorded / scheduled | Local + Phoenix audited | Reserved requests / cap |",
             "|---|---|---:|---:|---:|"]
    for backend, label in (("siwc", "Sol"), ("ollama", "Qwen")):
        item = data["backends"][backend]
        requests = item["reserved_requests"]
        cap = item["request_cap"]
        lines.append(f"| {label} | {item['status']} | {item['recorded_rows']}/40 | "
                     f"{item['audited_rows']} | {requests if requests is not None else 'unknown'} / "
                     f"{cap if cap is not None else 'unknown'} |")
    lines += ["", "Recorded rows can include a row awaiting its audit. Reserved requests can include",
              "an in-flight or failed request; they are not generated-token totals. Unfinished",
              "cells are not assumed to pass. These counts do not establish process liveness.", ""]
    for backend, label in (("siwc", "Sol"), ("ollama", "Qwen")):
        item = data["backends"][backend]
        review = item["clarification_review"]
        lines.append(f"- **{label}:** clarification reviews passed {review['passed']}/4; "
                     f"failed {review['failed']}; recorded answers pending/invalid review "
                     f"{review['pending_or_invalid']}. Answers for unrecorded cells remain unreviewed.")
    lines += ["", "| Backend / condition | Audited automatic passes / recorded | Recorded requests | Native operations |",
              "|---|---:|---:|---:|"]
    for backend, label in (("siwc", "Sol"), ("ollama", "Qwen")):
        item = data["backends"][backend]
        for condition, counts in item["conditions"].items():
            lines.append(f"| {label} / {condition} | {counts['audited_automatic_primary_passes']}/"
                         f"{counts['recorded_rows']} | {counts['recorded_model_requests']} | "
                         f"{counts['recorded_native_operations']} |")
    lines += ["", f"Supervisor's saved phase: `{data['operator_phase']}`. "
              f"Frozen source check: {data['frozen_files']} files; "
              f"{len(data['freeze_mismatches'])} mismatches.", "",
              "The automatic primary-pass count is separate from required clarification review.",
              "A final M4 decision also requires the frozen paired analysis and limits/audit checks.",
              "Refresh with `python -m tools.project_context --refresh`; narrative sections still",
              "need review when the study or roadmap changes."]
    if data["freeze_mismatches"]:
        lines += ["", "**Source mismatch: do not interpret this as an unchanged frozen run.**"]
    return "\n".join(lines)


def atomic_write(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def check_links():
    text = MASTER.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    links = re.findall(r"\[[^\]]+\]\(([^\s]+)\)", text)
    errors = []
    for target in links:
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        if not (MASTER.parent / unquote(parts.path)).exists():
            errors.append(target)
    print(json.dumps({"markdown_links_checked": len(links), "missing_local_targets": errors}, indent=2))
    return not errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--check", action="store_true", help="check local master-document link targets")
    args = parser.parse_args()
    if args.refresh:
        data = snapshot()
        text = MASTER.read_text(encoding="utf-8")
        if text.count(START) != 1 or text.count(END) != 1:
            raise ValueError("Expected exactly one project status block")
        before, rest = text.split(START)
        _, after = rest.split(END)
        atomic_write(ROOT / "PROJECT_LIVE_STATUS.json", json.dumps(data, indent=2) + "\n")
        atomic_write(MASTER, before + START + "\n" + render(data) + "\n" + END + after)
        print("Updated master status block and PROJECT_LIVE_STATUS.json; experiment files unchanged.")
    if args.check and not check_links():
        raise SystemExit(1)
    if not args.refresh and not args.check:
        parser.print_help()


if __name__ == "__main__":
    main()
