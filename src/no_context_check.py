"""Ask every question WITHOUT any passages.

If the model already answers a question correctly from memory, that question does not test retrieval.
Result goes to results/no_context.json (used later to report a 'retrieval-dependent' subset).
"""
import json
from pathlib import Path

import config
import llm
from judge import rule_pass
from questions import load_questions

RESULTS = Path(__file__).parent.parent / "results"
SYSTEM = ("Answer the question about Python from your own knowledge in one or two sentences. "
          "If you do not know, say that you do not know.")

if __name__ == "__main__":
    rows = []
    for q in load_questions():
        result = llm.ask([{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": q["question"]}],
                         config.ANSWER_MODEL, max_tokens=400, reasoning_effort=config.ANSWER_EFFORT)
        ok = rule_pass(q, result["text"] or "")
        rows.append({"id": q["id"], "answerable": q["answerable"], "correct_without_docs": ok,
                     "answer": result["text"], "total_tokens": result["total_tokens"]})
        print(q["id"], "correct without docs:" , ok)
    answerable = [r for r in rows if r["answerable"]]
    out = {
        "answered_without_docs": [r["id"] for r in answerable if r["correct_without_docs"]],
        "needs_docs": [r["id"] for r in answerable if not r["correct_without_docs"]],
        "details": rows,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "no_context.json").write_text(json.dumps(out, indent=2))
    print("\nanswered without docs:", out["answered_without_docs"])
    print("need the docs:", out["needs_docs"])
