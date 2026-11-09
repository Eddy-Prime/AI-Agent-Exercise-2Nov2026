# AI tools used

I used two AI assistants for this exercise: **Claude** (Anthropic) and **ChatGPT** (OpenAI).

## How I used them

- **Planning:** Claude helped plan the exercise: which techniques to describe, which two to test the experiment design and the schedule.
- **Explanations:** Claude and ChatGPT explained concepts (tokens, caching, chunking, top-k, reasoning tokens, LLM judges) so that I can explain them myself, Since i wasn't familiar with this.
- **Code:** I wrote the codes ` src/` and in some of the ` tests/`(API call, token counts, latency). Claude reviewed it, helped fix it, and gave better solution or approaches.
- **Data:** Claude drafted the 20 questions in `data/questions.jsonl` from those pages i found. A test checks that every evidence phrase exists in the pages.
- **Report:** I wrote the notes for Sections A and B in my own words. Claude fixed grammar and added some sentences, which I reviewed and kept or changed.

## How I checked the work

- The tests in `tests/` all pass (`python -m pytest`).
- Token counts come from the API's `usage` fields, not from my own counting.
