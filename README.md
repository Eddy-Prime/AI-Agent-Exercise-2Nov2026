# Token-efficient AI agent: small experiment

Technical exercise for the imec internship "Token-Efficient AI-Agent Design for an Operational Knowledge Hub".
The report is in `report/` (PDF). This repo contains the proof of concept behind it.

## What it does

A small documentation assistant answers questions from 7 pages of the Python 3.14 documentation.
We compare a **baseline agent** with token-optimized agents and measure tokens and answer quality:

| Variant | What changes |
|---|---|
| baseline | chunks of about 300 words, top-k 8, normal prompt, no output limit |
| A (retrieval tuning) | smaller chunks and a lower top-k, chosen with a retrieval sweep on the dev questions |
| B (output control) | concise-answer instruction and a `max_tokens` limit |
| A+B | both |

Tokens come from the API's `usage` numbers. Quality is checked three ways: retrieval hit rate, an automatic
key-fact check, and an LLM judge (a different model from the one that answers).

## Setup

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then put your own Groq API key in .env
```

## Run

```
python -m pytest                 # tests
python src/no_context_check.py   # ask the questions with no documents (finds questions the model already knows)
python src/retrieval_sweep.py    # choose chunk size / top-k on the dev questions (no LLM calls)
python src/run_experiment.py     # compare the four agents on the test questions
```

Every API call is cached in `results/cache/`, so running again costs no tokens.
Groq's free plan allows about 8K tokens per minute, so a full run takes roughly 30 minutes.

## Layout

```
data/docs/           the 7 documentation pages (source URL and fetch date at the top of each file)
data/questions.jsonl 20 questions: 8 dev (choose settings), 12 test (final comparison)
src/                 llm.py (API wrapper), ingest.py, retrieve.py, agent.py, judge.py, scripts
tests/               automatic tests
results/             raw runs, summary tables, retrieval sweep, manual check sheet
AI_USAGE.md          how AI tools were used
```

## Results

See `results/summary.md` and the report.

## Report
The report is in `report/Report.pdf` (source text: `report/draft.md`, built with `python report/build_pdf.py`).
