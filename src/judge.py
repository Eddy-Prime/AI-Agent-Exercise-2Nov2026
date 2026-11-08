import config
import llm
from retrieve import normalize

ABSTAIN_PHRASES = [
    "not in the documents", "not in the provided", "not mentioned", "does not say",
    "doesn't say", "does not specify", "doesn't specify", "not specified",
    "no information", "not provided", "cannot find", "can't find", "not stated",
    "does not contain", "doesn't contain", "don't know", "do not know",
    "not available", "not documented", "not covered", "not given",
    "do not contain", "not contain", "do not specify", "not present", "no mention",
]


def must_contain_pass(answer, must_contain):
    text = normalize(answer)
    return all(normalize(m) in text for m in must_contain)


def abstains(answer):
    text = normalize(answer)
    return any(phrase in text for phrase in ABSTAIN_PHRASES)


def rule_pass(question, answer):
    """Automatic check: key facts present (answerable) or a 'not in the documents' answer (unanswerable)."""
    if not question["answerable"]:
        return abstains(answer)
    return must_contain_pass(answer, question["must_contain"])


JUDGE_PROMPT = """You are grading an answer to a question about the Python documentation.

Question: {question}
Reference answer: {gold}
Candidate answer: {answer}

Is the candidate answer correct, meaning it agrees with the reference answer on the key facts? Extra detail is fine. Reply with exactly one word: CORRECT or INCORRECT."""


def llm_judge(question, answer):
    """Ask a second model to grade the answer. Returns (True/False/None, raw judge result)."""
    if not answer or not answer.strip():
        return False, None
    if question["answerable"]:
        gold = question["gold_answer"]
    else:
        gold = ("The documents do not contain this information. "
                "A correct answer says that the information is not available.")
    prompt = JUDGE_PROMPT.format(question=question["question"], gold=gold, answer=answer)
    result = llm.ask([{"role": "user", "content": prompt}], config.JUDGE_MODEL,
                     max_tokens=200, reasoning_effort=config.JUDGE_EFFORT)
    verdict = (result["text"] or "").strip().upper()
    if verdict.startswith("INCORRECT"):
        return False, result
    if verdict.startswith("CORRECT"):
        return True, result
    return None, result
