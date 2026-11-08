"""Retrieval sweep on the DEV questions. No LLM calls: it only checks whether the right text is retrieved.

For each setting we measure
  hit rate   = share of answerable dev questions whose evidence is inside the retrieved text
  avg words  = average number of words retrieved (a stand-in for input tokens)
Choice rule: highest hit rate first, then the fewest retrieved words.
"""
import csv
import json
from itertools import product
from pathlib import Path

from ingest import word_count
from questions import load_questions
from retrieve import evidence_hit
import agent

RESULTS = Path(__file__).parent.parent / "results"
CHUNK_WORDS = [100, 150, 200, 300]
TOP_K = [1, 2, 3, 4, 5, 8]
THRESHOLDS = [0.0, 0.05, 0.10]


def run_sweep():
    questions = [q for q in load_questions("dev") if q["answerable"]]
    rows = []
    for chunk_words, top_k, threshold in product(CHUNK_WORDS, TOP_K, THRESHOLDS):
        retriever = agent.get_retriever(chunk_words)
        hits, words = 0, 0
        for q in questions:
            retrieved = retriever.search(q["question"], top_k, threshold)
            hits += bool(evidence_hit(retrieved, q["evidence"]))
            words += sum(word_count(r["text"]) for r in retrieved)
        rows.append({"chunk_words": chunk_words, "top_k": top_k, "threshold": threshold,
                     "hit_rate": round(hits / len(questions), 3),
                     "avg_words": round(words / len(questions), 1)})
    return rows


def choose(rows):
    best = max(r["hit_rate"] for r in rows)
    candidates = [r for r in rows if r["hit_rate"] == best]
    return min(candidates, key=lambda r: (r["avg_words"], r["top_k"]))


if __name__ == "__main__":
    rows = run_sweep()
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "retrieval_sweep.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    chosen = choose(rows)
    settings = {k: chosen[k] for k in ("chunk_words", "top_k", "threshold")}
    (RESULTS / "chosen_settings.json").write_text(json.dumps(settings, indent=2))
    base = next(r for r in rows if (r["chunk_words"], r["top_k"], r["threshold"]) == (300, 8, 0.0))
    print("baseline (300 words, top-k 8, no threshold):", base)
    print("chosen for variant A:", chosen)
    print("\ntop 10 by hit rate, then fewest words:")
    for r in sorted(rows, key=lambda r: (-r["hit_rate"], r["avg_words"]))[:10]:
        print(r)
