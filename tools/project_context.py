"""Refresh documentation from saved public checkpoints; never run experiments."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from statistics import median
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "PROJECT_MASTER_README.md"
EFFICIENCY = ROOT / "docs/M4_EFFICIENCY_AND_TIMING_2026-10-27.md"
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
    reviewed_passes = set()
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
            if review["pass"]:
                reviewed_passes.add(key)
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
            "known_input_tokens": sum(row["inference"]["known_input_tokens"] for row in subset),
            "known_output_tokens": sum(row["inference"]["known_output_tokens"] for row in subset),
            "usage_incomplete_rows": sum(not row["inference"]["usage_complete"] for row in subset),
            "task_wall_seconds": sum(row["wall_seconds"] for row in subset),
            "mean_task_seconds": (sum(row["wall_seconds"] for row in subset) / len(subset)
                                  if subset else None),
            "median_task_seconds": median(row["wall_seconds"] for row in subset) if subset else None,
        }
    pairs = {}
    for row in rows:
        pairs.setdefault((row["case"], row["repetition"]), {})[row["condition"]] = row
    matched = [pair for pair in pairs.values() if set(pair) == {"primitives", "macro"}
               and all(audit_pass(row) and row.get("primary_pass") is True
                       and (row["case"] != "ambiguous_goal"
                            or backend + "/" + row["job"]["id"] in reviewed_passes)
                       for row in pair.values())]
    matched_costs = {
        condition: {
            "model_requests": sum(pair[condition]["inference"]["calls"] for pair in matched),
            "native_operations": sum(pair[condition]["score"]["native_operations"] for pair in matched),
            "task_wall_seconds": sum(pair[condition]["wall_seconds"] for pair in matched),
        }
        for condition in ("primitives", "macro")
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
        "review_qualified_matched_success_pairs": len(matched),
        "matched_success_costs": matched_costs,
        "saved_campaign_elapsed_seconds": checkpoint.get("campaign", {}).get("elapsed_seconds"),
        "closed_total_elapsed_seconds": checkpoint.get("total_elapsed_seconds"),
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
        "snapshot_at": datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S"),
        "scope": "Saved checkpoint snapshot, not a live process probe or final research verdict",
        "operator_phase": read_json(LIVE / "operator/status.json").get("phase", "unavailable"),
        "frozen_files": len(freeze.get("files", {})),
        "freeze_mismatches": mismatches,
        "closeout": read_json(LIVE / "closeout.json") or None,
        "m5": read_json(ROOT / "artifacts/macro-m5-20261027/status.json") or None,
        "backends": {backend: backend_status(backend, reviews) for backend in ("siwc", "ollama")},
    }


def render(data):
    backends = data["backends"]
    recorded = sum(b["recorded_rows"] for b in backends.values())
    execution_complete = all(b["execution_and_audits_complete"] for b in backends.values())
    stopped = [name for name, b in backends.items() if b["status"] not in ("COMPLETE", "RUNNING")]
    reviews_done = sum(b["clarification_review"]["passed"] + b["clarification_review"]["failed"]
                       for b in backends.values())
    closure = data.get("closeout") or {}
    closed = execution_complete and reviews_done == 8 and closure.get("study_complete") is True
    phase = ("closed with mixed findings" if closed else
             "execution closed; final interpretation pending" if execution_complete else
             "execution incomplete; inspect stopped/unstarted backend" if stopped else
             "live execution in progress")
    decision = (closure['decision'] if closed else
                'Bounded macro remains the engineering candidate. Final M4 retention and M5 progression require the completed evidence and interpretation.')
    next_action = (closure['next_action'] if closed else
                   'Finish/inspect the frozen execution; review required clarification transcripts; reconcile correctness, efficiency, faults, audits and bounds; document the retention decision and M5 next steps.')
    gates = ('M4 execution, audits and review are closed. Qwen failed retention; this is a documented limitation, not an unfinished trial. M5 is not started.' if closed else
             'Incomplete execution or review remains an open gate. Saved RUNNING status alone does not rule out an external service/process problem.')
    m5 = data.get('m5')
    current_milestone = f'M4: {phase}.'
    if m5:
        current_milestone = f"M5: {m5['status']}. {m5['current_work']}"
        next_action = m5['next_actions']
        gates = '; '.join(f'{name}: {state}' for name, state in m5['gates'].items()) + '. ' + m5['human_review']
    lines = [f"Last refreshed: **{data['snapshot_at']}**. Saved-checkpoint snapshot.", "",
             "### Current work and next actions", "",
             "| Progress item | Current evidence / action |",
             "|---|---|",
             f"| Current milestone | {current_milestone} |",
             f"| M4 recorded execution | {recorded}/80 trial rows; {80 - recorded} cells without a recorded result, including any in-flight trial. |",
             f"| M4 operator clarification review | {reviews_done}/8 valid operator reviews recorded; {8 - reviews_done} still required. This is not independent human adjudication. |",
             f"| Current decision | {decision} |",
             f"| Next actions | {next_action} |",
             f"| Open gates / blockers | {gates} |", "",
             "| Backend | Saved status | Recorded / scheduled | Local + Phoenix audited | Reserved requests / cap |",
             "|---|---|---:|---:|---:|"]
    for backend, label in (("siwc", "Sol"), ("ollama", "Qwen")):
        item = data["backends"][backend]
        requests = item["reserved_requests"]
        cap = item["request_cap"]
        lines.append(f"| {label} | {item['status']} | {item['recorded_rows']}/40 | "
                     f"{item['audited_rows']} | {requests if requests is not None else 'unknown'} / "
                     f"{cap if cap is not None else 'unknown'} |")
    if m5:
        lines += ["", f"M5 separately used **{m5['demo_model_requests']} presentation inference requests** "
                  f"and **{m5['new_research_trials']} new research trials**. Independent human ratings are "
                  "deferred by user choice; the [eight-case packet](artifacts/macro-m5-20261027/ROSA_M5_HUMAN_REVIEW_PACKET.zip) "
                  "is ready. The eight operator ratings above do not count as human review."]
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
    if closed:
        lines += ["", "The supervisor phase above is its preserved pre-review checkpoint. Final closure",
                  "is recorded in `closeout.json` and the [final M4 report](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md).",
                  "Completed review includes four failed Qwen clarification cases; eight reviews does not mean eight passes."]
    if data["freeze_mismatches"]:
        lines += ["", "**Source mismatch: do not interpret this as an unchanged frozen run.**"]
    return "\n".join(lines)


def efficiency_report(data):
    def number(value):
        return f"{value:,.2f}" if value is not None else "unavailable"

    def reduction(reference, candidate):
        return f"{100 * (1 - candidate / reference):+.1f}%" if reference else "unavailable"

    final = (data.get("closeout") or {}).get("study_complete") is True
    lines = ["# M4 final efficiency and timing" if final else "# M4 efficiency and timing checkpoint", "",
             f"Date: **{data['snapshot_date']}**. Derived from saved trial rows; no new inference.", "",
             "Positive reduction means less resource use or time in macro mode. Correctness and",
             "review completeness must be considered alongside savings. Partial runs are not final results.", "",
             "| Backend / condition | Recorded /20 | Audited automatic passes | Requests | Native ops | Known input tokens | Known output tokens | Incomplete-usage rows |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for backend, label in (("siwc", "Sol"), ("ollama", "Qwen")):
        for condition, c in data["backends"][backend]["conditions"].items():
            lines.append(f"| {label} / {condition} | {c['recorded_rows']}/20 | "
                         f"{c['audited_automatic_primary_passes']} | {c['recorded_model_requests']} | "
                         f"{c['recorded_native_operations']} | {c['known_input_tokens']:,} | "
                         f"{c['known_output_tokens']:,} | {c['usage_incomplete_rows']} |")
    lines += ["", "| Backend / condition | Total recorded task seconds | Mean seconds/task | Median seconds/task |",
              "|---|---:|---:|---:|"]
    for backend, label in (("siwc", "Sol"), ("ollama", "Qwen")):
        for condition, c in data["backends"][backend]["conditions"].items():
            lines.append(f"| {label} / {condition} | {number(c['task_wall_seconds'])} | "
                         f"{number(c['mean_task_seconds'])} | {number(c['median_task_seconds'])} |")
    lines += ["", "These tables include unsuccessful recorded attempts. An early failure can look fast",
              "or cheap. They exclude any request still in flight without a recorded task result;",
              "the master checkpoint separately reports campaign reservations. Unknown token usage",
              "is not zero; known totals are lower bounds where usage is incomplete.", "",
              "## Same-case pairs where both conditions passed", "",
              "This descriptive subset requires both audits and valid recorded clarification reviews",
              "when applicable. Pending/failed clarification reviews exclude that pair. It supplements",
              "all-attempt accounting and is not the final frozen engineering-screen decision.", "",
              "| Backend | Saved status | Qualifying pairs /20 | Requests primitives → macro | Request reduction | Native ops primitives → macro | Native reduction | Task seconds primitives → macro | Time reduction |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for backend, label in (("siwc", "Sol"), ("ollama", "Qwen")):
        b = data["backends"][backend]
        p, m = b["matched_success_costs"]["primitives"], b["matched_success_costs"]["macro"]
        lines.append(f"| {label} | {b['status']} | {b['review_qualified_matched_success_pairs']}/20 | "
                     f"{p['model_requests']} → {m['model_requests']} | "
                     f"{reduction(p['model_requests'], m['model_requests'])} | "
                     f"{p['native_operations']} → {m['native_operations']} | "
                     f"{reduction(p['native_operations'], m['native_operations'])} | "
                     f"{number(p['task_wall_seconds'])} → {number(m['task_wall_seconds'])} | "
                     f"{reduction(p['task_wall_seconds'], m['task_wall_seconds'])} |")
    lines += ["", "## Campaign time and measurement limits", ""]
    for backend, label in (("siwc", "Sol"), ("ollama", "Qwen")):
        b = data["backends"][backend]
        closed = b["closed_total_elapsed_seconds"]
        elapsed = closed if closed is not None else b["saved_campaign_elapsed_seconds"]
        state = "closed backend run" if closed is not None else "saved elapsed checkpoint; still incomplete"
        minutes = f"{elapsed / 60:.2f}" if elapsed is not None else "unavailable"
        lines.append(f"- {label}: **{minutes} minutes** ({number(elapsed)} seconds), {state}.")
    lines += ["", "Task wall time covers the bounded model/tool loop, including waits and recovery.",
              "It excludes simulator setup/reset, outside-task independent scoring observations and",
              "persisted trace audits. Backend elapsed time also includes those overheads and, when",
              "closed, cleanup; it does not include waiting for the other backend's serialized turn.",
              "Means and medians cover recorded rows only; incomplete trials can distort comparisons.",
              "All-attempt costs and final reporting must retain infrastructure-censored attempts too.", "",
              "Compare architecture within each backend first. Qwen runs on the laptop with partial",
              "CPU/GPU offload; Sol uses a remote service with different sampling, tokenization and",
              "compute. Observed elapsed-time differences describe this setup, not a controlled",
              "hardware-independent model-speed ranking. No energy, dollar cost or pure generation",
              "tokens/second was measured by these task-wall aggregates.", "",
              "Regenerate with `python -m tools.project_context --refresh`. The frozen experiment",
              "runner and trial scores remain unchanged. Derived reports reflect the saved review overlay."]
    if final:
        lines += ["", "Execution and all required reviews are complete. See the",
                  "[final M4 report](../artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md)",
                  "for the screen decision: Sol passes; Qwen fails the correctness condition despite savings."]
    else:
        lines += ["The final M4 report should include these measures using the completed schedule and required review overlay."]
    return "\n".join(lines) + "\n"


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
        atomic_write(EFFICIENCY, efficiency_report(data))
        atomic_write(MASTER, before + START + "\n" + render(data) + "\n" + END + after)
        print("Updated master status, JSON snapshot and efficiency/timing report; experiment files unchanged.")
    if args.check and not check_links():
        raise SystemExit(1)
    if not args.refresh and not args.check:
        parser.print_help()


if __name__ == "__main__":
    main()
