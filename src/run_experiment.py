"""Run the four agents on the TEST questions and compare tokens and answer quality.

Output (in results/): raw_runs.jsonl, summary.csv, summary.md, manual_check.csv
Every API call is cached on disk, so running this again costs no tokens.
"""
import csv
import json
import sys
from pathlib import Path

import agent
import judge
from ingest import word_count
from questions import load_questions
from retrieve import evidence_hit

RESULTS = Path(__file__).parent.parent / "results"


def load_json(name, default):
    path = RESULTS / name
    return json.loads(path.read_text()) if path.exists() else default


def run(split="test"):
    settings_a = load_json("chosen_settings.json", None)
    if settings_a is None:
        sys.exit("Run src/retrieval_sweep.py first (it writes results/chosen_settings.json).")
    variants = agent.make_variants(settings_a)
    rows = []
    for name, settings in variants.items():
        for q in load_questions(split):
            out = agent.answer(q["question"], settings)
            text = out["text"] or ""
            judged, _ = judge.llm_judge(q, text)
            rows.append({
                "variant": name, "id": q["id"], "type": q["type"], "question": q["question"],
                "gold_answer": q["gold_answer"], "answer": text,
                "finish_reason": out["finish_reason"],
                "prompt_tokens": out["prompt_tokens"], "completion_tokens": out["completion_tokens"],
                "total_tokens": out["total_tokens"], "latency_s": round(out["latency_s"], 3),
                "retrieved_ids": [p["id"] for p in out["passages"]],
                "retrieved_words": sum(word_count(p["text"]) for p in out["passages"]),
                "hit": evidence_hit(out["passages"], q["evidence"]),
                "rule_pass": judge.rule_pass(q, text), "judge_pass": judged,
            })
            print(name, q["id"], "tokens", out["total_tokens"], "rule", rows[-1]["rule_pass"],
                  "judge", judged, "cached" if out["cached"] else "")
    return rows, settings_a


def mean(values):
    values = list(values)
    return round(sum(values) / len(values), 1) if values else 0


def summarize(rows):
    needs_docs = set(load_json("no_context.json", {}).get("needs_docs", []))
    baseline_total = None
    summary = []
    for name in dict.fromkeys(r["variant"] for r in rows):
        rs = [r for r in rows if r["variant"] == name]
        answerable = [r for r in rs if r["type"] != "unanswerable"]
        correct = lambda r: r["judge_pass"] if r["judge_pass"] is not None else r["rule_pass"]
        dependent = [r for r in rs if r["id"] in needs_docs]
        row = {
            "variant": name, "questions": len(rs),
            "hit_rate": f"{sum(bool(r['hit']) for r in answerable)}/{len(answerable)}",
            "avg_prompt_tokens": mean(r["prompt_tokens"] for r in rs),
            "avg_completion_tokens": mean(r["completion_tokens"] for r in rs),
            "avg_total_tokens": mean(r["total_tokens"] for r in rs),
            "rule_correct": f"{sum(r['rule_pass'] for r in rs)}/{len(rs)}",
            "judge_correct": f"{sum(bool(correct(r)) for r in rs)}/{len(rs)}",
            "needs_docs_correct": f"{sum(bool(correct(r)) for r in dependent)}/{len(dependent)}",
            "cut_off": sum(r["finish_reason"] == "length" for r in rs),
            "avg_latency_s": mean(r["latency_s"] for r in rs),
        }
        if baseline_total is None:
            baseline_total = row["avg_total_tokens"]
        row["tokens_vs_baseline"] = f"{round(100 * (row['avg_total_tokens'] / baseline_total - 1))}%"
        summary.append(row)
    return summary


def write_outputs(rows, summary):
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "raw_runs.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(RESULTS / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)
    cols = list(summary[0].keys())
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(s[c]) for c in cols) + " |" for s in summary]
    (RESULTS / "summary.md").write_text("\n".join(lines) + "\n")
    # File for the manual check: fill in the human_pass column yourself
    with open(RESULTS / "manual_check.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["variant", "id", "question", "gold_answer", "answer",
                         "rule_pass", "judge_pass", "human_pass"])
        for r in rows:
            writer.writerow([r["variant"], r["id"], r["question"], r["gold_answer"],
                             r["answer"], r["rule_pass"], r["judge_pass"], ""])
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    rows, _ = run(sys.argv[1] if len(sys.argv) > 1 else "test")
    write_outputs(rows, summarize(rows))
