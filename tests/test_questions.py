from collections import Counter
from pathlib import Path

from questions import load_questions
from retrieve import normalize

DOCS = Path(__file__).parent.parent / "data" / "docs"


def test_counts_and_split():
    qs = load_questions()
    assert len(qs) == 20
    assert Counter(q["split"] for q in qs) == {"dev": 8, "test": 12}
    assert Counter(q["type"] for q in qs) == {"simple": 14, "multi": 3, "unanswerable": 3}
    assert len({q["id"] for q in qs}) == 20


def test_every_evidence_phrase_exists_in_a_gold_source():
    for q in load_questions():
        if not q["answerable"]:
            assert q["evidence"] == [] and q["gold_sources"] == []
            continue
        texts = [normalize((DOCS / s).read_text()) for s in q["gold_sources"]]
        assert texts, q["id"]
        for phrase in q["evidence"]:
            assert any(normalize(phrase) in t for t in texts), (q["id"], phrase)


def test_must_contain_facts_are_in_the_gold_answer():
    for q in load_questions():
        if q["answerable"]:
            gold = normalize(q["gold_answer"])
            for m in q["must_contain"]:
                assert normalize(m) in gold, (q["id"], m)
