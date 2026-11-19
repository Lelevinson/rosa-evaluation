"""F1 step 0: classify Qwen length-stop trials (read-only, offline, deterministic).

Usage (from the rosa-evaluation root):
    python -I -B tools/f1/length_stops.py [--root .] [--json]

Reads retained trial files only:
  * M4 Gazebo Qwen:  artifacts/macro-m4-20261027/ollama/*/{result,trace}.json
  * G1 Qwen lab:     artifacts/macro-generalization-20261113/revision-1/
                     stage-4-qwen-lab-20261119/trials/*/result.json

A length stop is an inference event with finish_reason == "length".
Nothing is written; output goes to stdout. No network, no clock, no randomness.

Classification rule (applied in order; the first match is the primary class):
  A  downstream of a wrong selection or blocked action:
     a select_skill call happened before the capped call AND either the scorer
     marks selection incorrect (G1) or the capped call's context contains a
     rejected tool result (M4/G1).
  B  repetition loop: some sentence of >= 40 characters occurs >= 3 times
     verbatim (whitespace-normalised) in the truncated output.
  C  long analysis / rambling: the truncated output is prose with no tool call
     and neither A nor B applies.
  D  other.
Secondary flags (repetition count, whether the output names the expected
skill) are reported alongside so the primary class can be audited.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

M4_DIR = Path("artifacts/macro-m4-20261027/ollama")
G1_DIR = Path("artifacts/macro-generalization-20261113/revision-1/stage-4-qwen-lab-20261119/trials")
TAIL_CHARS = 1200  # ~300 tokens at ~4 characters/token; tokenizer not used (approximation)
def rejection_codes(obj) -> list[str]:
    """Collect `code` values of tool results marked rejected, anywhere in a JSON structure.

    Tool results are stored as JSON strings inside message content, so strings
    that look like JSON objects are parsed and searched too.
    """
    found: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("rejected") is True and isinstance(o.get("code"), str):
                found.add(o["code"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str) and o.lstrip().startswith("{"):
            try:
                walk(json.loads(o))
            except ValueError:
                pass

    walk(obj)
    return sorted(found)


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def sentences(text: str):
    parts = re.split(r"(?<=[.!?:])\s+|\n+", text)
    return [re.sub(r"\s+", " ", s).strip() for s in parts if len(s.strip()) >= 40]


def max_repeat(text: str):
    counts: dict[str, int] = {}
    for s in sentences(text):
        counts[s] = counts.get(s, 0) + 1
    if not counts:
        return 0, ""
    best = max(sorted(counts), key=lambda k: counts[k])
    return counts[best], best


def cap_kind(events, k):
    """Which limit truncated the call: the 1,024 per-call cap, or the remaining 2,048 per-task allowance."""
    req = events[k].get("requested_output_allowance")
    prior = sum((e.get("usage") or {}).get("output_tokens", 0) for e in events[:k])
    if req == 1024:
        return f"per-call 1024 (task total before: {prior})"
    return f"task budget: {req} left of 2048 (used {prior})"


def classify(selected_before: bool, selection_wrong: bool | None, rejections: list[str], text: str, has_tool_call: bool):
    rep, _ = max_repeat(text)
    if selected_before and (selection_wrong or rejections):
        return "A", rep
    if rep >= 3:
        return "B", rep
    if not has_tool_call and text.strip():
        return "C", rep
    return "D", rep


def g1_rows(root: Path):
    rows = []
    for p in sorted((root / G1_DIR).glob("*/result.json")):
        r = load(p)
        ev = r["inference"]["events"]
        idx = [i for i, e in enumerate(ev) if e.get("finish_reason") == "length"]
        if not idx:
            continue
        k = idx[0]
        out = r["model_outputs"][k]
        text = out.get("content", "") or ""
        prior_tools = [t["tool"] + ":" + t["input"] for t in (r.get("tool_inputs") or [])]
        selects = [t for t in (r.get("tool_inputs") or []) if t["tool"] == "select_skill"]
        selected = selects[0]["input"] if selects else "(none)"
        mi = r.get("model_inputs") or []
        rejections = rejection_codes(mi[k]) if len(mi) > k else []
        expected = r["case"].get("skill_id")
        sel_wrong = r["score"].get("selection_correct") is False
        cls, rep = classify(bool(selects), sel_wrong if selects else None, rejections, text, bool(out.get("tool_calls")))
        rows.append({
            "study": "G1", "trial": r["id"], "condition": r["mode"], "task": f"{r['case']['domain']}/{r['case']['kind']}",
            "request": r["case"]["request"], "expected_skill": expected or "(clarify)",
            "selected": selected, "cap_call": f"{k + 1}/{len(ev)}", "cap_kind": cap_kind(ev, k), "tools_before_cap": prior_tools,
            "rejections_in_context": rejections, "output_tokens": out.get("usage_metadata", {}).get("output_tokens"),
            "names_expected_skill": bool(expected) and expected in text, "max_sentence_repeat": rep,
            "class": cls, "tail": text[-TAIL_CHARS:],
        })
    return rows


def m4_rows(root: Path):
    rows = []
    base = root / M4_DIR
    for d in sorted(x for x in base.iterdir() if (x / "result.json").exists()):
        r = load(d / "result.json")
        ev = r["inference"]["events"]
        idx = [i for i, e in enumerate(ev) if e.get("finish_reason") == "length"]
        if not idx:
            continue
        k = idx[0]
        spans = load(d / "trace.json")["spans"]
        llm = sorted((s for s in spans if s["attributes"].get("openinference.span.kind") == "LLM"), key=lambda s: s["start_time"])
        cap = llm[k]
        cap_start = cap["start_time"]
        tools = sorted((s for s in spans if s["attributes"].get("openinference.span.kind") == "TOOL" and s["start_time"] < cap_start),
                       key=lambda s: s["start_time"])
        prior_tools = [f"{s['name']}:{s['attributes'].get('input.value')}" for s in tools]
        selects = [s["attributes"].get("input.value") for s in tools if s["name"] == "select_skill"]
        text = cap["attributes"].get("llm.output_messages.0.message.content", "") or ""
        rejections = rejection_codes([v for kk, v in sorted(cap["attributes"].items()) if kk.startswith("llm.input_messages.")])
        cls, rep = classify(bool(selects), None, rejections, text, False)
        rows.append({
            "study": "M4", "trial": d.name, "condition": r["condition"], "task": f"ur5e/{r['case']}",
            "request": r["request"], "expected_skill": "(not recorded in result.json)",
            "selected": selects[0] if selects else "(none)", "cap_call": f"{k + 1}/{len(ev)}", "cap_kind": cap_kind(ev, k),
            "tools_before_cap": prior_tools, "rejections_in_context": rejections,
            "output_tokens": ev[k].get("usage", {}).get("output_tokens"),
            "names_expected_skill": None, "max_sentence_repeat": rep, "class": cls, "tail": text[-TAIL_CHARS:],
        })
    return rows


def render(rows):
    out = ["| Study | Trial | Cond. | Task | Selected before cap | Cap at call | Limit hit | Rejections fed to capped call | Max sentence repeat | Class |",
           "|---|---|---|---|---|---|---|---|---:|---|"]
    for x in rows:
        out.append(f"| {x['study']} | {x['trial']} | {x['condition']} | {x['task']} | `{x['selected']}` | {x['cap_call']} | {x['cap_kind']} | "
                   f"{', '.join(x['rejections_in_context']) or 'none'} | {x['max_sentence_repeat']} | **{x['class']}** |")
    tally: dict[str, int] = {}
    for x in rows:
        tally[x["class"]] = tally.get(x["class"], 0) + 1
    out += ["", "Totals: " + ", ".join(f"{c}={tally[c]}" for c in sorted(tally)) + f" (n={len(rows)})", ""]
    for x in rows:
        out += [f"### {x['study']} {x['trial']} — class {x['class']}", "",
                f"- Request: {x['request']}", f"- Expected skill: {x['expected_skill']}",
                f"- Tools before cap: {'; '.join(x['tools_before_cap']) or 'none'}",
                f"- Output tokens on capped call: {x['output_tokens']}",
                f"- Output names expected skill: {x['names_expected_skill']}", "",
                f"Last ~{TAIL_CHARS} characters (~300 tokens, approximate):", "", "```text", x["tail"].strip(), "```", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="rosa-evaluation root")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    a = ap.parse_args()
    root = Path(a.root)
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")  # same bytes on every console
    rows = m4_rows(root) + g1_rows(root)
    print(json.dumps(rows, indent=1, sort_keys=True) if a.json else render(rows))


if __name__ == "__main__":
    main()
