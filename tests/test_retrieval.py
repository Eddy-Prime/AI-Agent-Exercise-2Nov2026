from retrieve import Retriever, evidence_hit

CHUNKS = [
    {"id": "a#0", "source": "a.md", "text": "Set the PYTHON_DISABLE_REMOTE_DEBUG environment variable to 1"},
    {"id": "b#0", "source": "b.md", "text": "The Template class describes the contents of a template string"},
    {"id": "c#0", "source": "c.md", "text": "Queues are shared between interpreters with memoryview"},
]


def test_best_match_is_first():
    results = Retriever(CHUNKS).search("how to disable remote debug environment variable", top_k=3)
    assert results[0]["id"] == "a#0"


def test_top_k_limits_results():
    assert len(Retriever(CHUNKS).search("template string interpreters", top_k=1)) == 1


def test_threshold_removes_weak_matches():
    r = Retriever(CHUNKS)
    all_results = r.search("template string", top_k=3, threshold=0.0)
    strict = r.search("template string", top_k=3, threshold=0.9)
    assert len(strict) < len(all_results) or len(all_results) == 0


def test_no_match_returns_nothing():
    assert Retriever(CHUNKS).search("zebra giraffe", top_k=3) == []


def test_evidence_hit_ignores_case_and_spacing():
    retrieved = [CHUNKS[0]]
    assert evidence_hit(retrieved, ["python_disable_remote_debug   ENVIRONMENT variable"]) is True
    assert evidence_hit(retrieved, ["something else"]) is False
    assert evidence_hit(retrieved, []) is None
