import config
import llm
from ingest import load_chunks
from retrieve import Retriever

SYSTEM_BASELINE = (
    "You are a documentation assistant. Answer the question using only the passages provided. "
    "If the passages do not contain the answer, say that the information is not in the documents."
)
SYSTEM_CONCISE = SYSTEM_BASELINE + " Answer in at most two sentences and do not add an introduction."

BASELINE = {
    "chunk_words": config.BASELINE_CHUNK_WORDS,
    "top_k": config.BASELINE_TOP_K,
    "threshold": config.BASELINE_THRESHOLD,
    "concise": False,
    "max_tokens": None,
}

_retrievers = {}


def get_retriever(chunk_words):
    if chunk_words not in _retrievers:
        _retrievers[chunk_words] = Retriever(load_chunks(chunk_words))
    return _retrievers[chunk_words]


def make_variants(retrieval_settings):
    """The four agents we compare. retrieval_settings: chunk_words, top_k, threshold for variant A."""
    a = {**BASELINE, **retrieval_settings}
    return {
        "baseline": BASELINE,
        "A": a,
        "B": {**BASELINE, "concise": True, "max_tokens": config.CONCISE_MAX_TOKENS},
        "A+B": {**a, "concise": True, "max_tokens": config.CONCISE_MAX_TOKENS},
    }


def build_messages(question, passages, concise):
    system = SYSTEM_CONCISE if concise else SYSTEM_BASELINE
    if passages:
        context = "\n\n".join(f"[{i}] ({p['source']})\n{p['text']}" for i, p in enumerate(passages, 1))
    else:
        context = "(no passages were retrieved)"
    user = f"Passages:\n{context}\n\nQuestion: {question}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def answer(question_text, settings):
    retriever = get_retriever(settings["chunk_words"])
    passages = retriever.search(question_text, settings["top_k"], settings["threshold"])
    messages = build_messages(question_text, passages, settings["concise"])
    result = llm.ask(messages, config.ANSWER_MODEL, max_tokens=settings["max_tokens"],
                     reasoning_effort=config.ANSWER_EFFORT)
    return {"passages": passages, **result}
