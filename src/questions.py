import json
from pathlib import Path

QUESTIONS_FILE = Path(__file__).parent.parent / "data" / "questions.jsonl"


def load_questions(split=None, path=QUESTIONS_FILE):
    questions = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    if split:
        questions = [q for q in questions if q["split"] == split]
    return questions
