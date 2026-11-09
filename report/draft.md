# Token-efficient AI agent: draft

## A. Techniques that reduce token usage

### Technique 1: Retrieval tuning
**Meaning:** Improving how the AI agent searches for and selects information before sending it to the AI model.

**How it works:** It reduces input tokens by sending only the necessary information instead of all the information.

**Reduces:** Input tokens. <!-- new -->

**Settings:**
- Top-k: retrieves the highest matching passages.
- Chunk size: how big each chunk (piece of a document) is.
- Similarity threshold: removes passages that match the question too weakly. <!-- new -->

**Benefit:** Fewer tokens are sent, so the cost is lower and responses are faster. <!-- new -->

**Possible disadvantages:**
- Leaving out important information.
- Adds more processing time.

### Technique 2: History management
**Meaning:** Sending the last 5 messages plus a short summary of the previous conversation, or the important information from earlier.

**How it saves tokens:** It sends fewer previous messages to the AI model, which helps lower API costs.

**Reduces:** Input tokens. <!-- new -->

**Risk:**
- The summary could leave out important information, causing the AI to forget or misunderstand earlier details.
- Creating the summary needs an extra model call. <!-- new -->

In short: reducing the conversation history saves tokens, but the AI could lose important context.

### Technique 3: Prompt compaction and prompt caching
**Prompt compaction:** Making the instructions or the context sent to the AI shorter while keeping the important meaning.
- Saves tokens: it reduces input tokens because shorter instructions are sent to the model.
- Risk: if too much is removed, the AI could misunderstand the requirements.

**Prompt caching:** Reusing the previous prompt content, so the provider does not have to process the same start of the prompt again. <!-- new -->
- It lowers cost and response time, but not the number of tokens. <!-- new -->
- Risk: it only helps when prompts repeat, and it depends on provider support. <!-- new -->
- Difference from disk caching: disk caching returns saved answers without making API calls.

### Technique 4: Output control
**Meaning:** Controlling how much text the AI generates in its responses.

**How it saves tokens:** It reduces output tokens. For example, a normal response is 200 tokens and a concise response is 80 tokens.

**What could go wrong:** Answers can be cut off when the limit is reached. If the maximum token limit (`max_tokens`) is too low, answers are too short to explain complicated information. Reasoning models also count their hidden thinking as output tokens, so a concise-answer instruction does not remove them. <!-- new -->

**Types of output control:**
- Concise-answer instructions for the AI.
- The token limit set in the settings.

### Technique 5: Model routing
**Meaning:** Selecting different AI models depending on how difficult the user's question is. For example:
- A smaller model for simple questions or tasks.
- A larger model for complex questions or tasks.

**How it saves:** This mainly saves money rather than tokens.

**Reduces:** Neither input nor output tokens directly. <!-- new -->

**Benefits:**
- Lower API cost for simpler questions.
- Potentially faster responses.

**Risk:** If a hard question is sent to the small model, the answer quality can drop. Choosing the model also adds a little extra cost and time. <!-- new -->

## B. The two techniques I would test first

### Technique 1: Retrieval tuning
**1. Why I chose it:** Because it helps retrieve the relevant, necessary information before it is given to the AI model. Retrieved passages are usually the biggest part of the input, so this is where the most tokens can be saved. <!-- new sentence -->

**2. How I would implement / evaluate it:** I would compare the baseline agent with the optimized agent, using the same test questions, and compare tokens and answer quality. I would change one setting at a time (top-k, chunk size, similarity threshold) and choose the settings on a small set of dev questions before comparing on separate test questions. <!-- second sentence new -->

**3. Metrics:** <!-- fixed: top-k and chunk size are settings, not metrics -->
- Input tokens per request, taken from the API usage numbers.
- Retrieval hit rate: whether the correct passage was retrieved.
- Answer correctness.
- Latency.

**4. How I check that quality did not drop:** I compare the answers of the baseline and the optimized agent on the same questions. I check that the correct passage is still retrieved (hit rate), that the answer contains the key facts, and that a second model (a judge) marks it correct. <!-- rewritten: tokens are not a quality check -->

### Technique 2: Output control
**1. Why I chose it:** Because we can control the text the AI generates, by giving instructions for concise responses and by limiting the number of tokens. It reduces the output side of the request and is easy to test. <!-- second sentence new -->

**2. How I would implement / evaluate it:** By asking the AI for concise answers in the instructions and by setting a maximum token limit (`max_tokens`). I would compare it with the baseline on the same questions. <!-- fixed: prompt caching and compaction belong to technique 3 -->

**3. Metrics:**
- Number of generated (output) tokens per answer, taken from the API usage numbers.
- Number of answers cut off by the token limit. <!-- new -->
- Latency. <!-- new -->

**4. How I check that quality did not drop:** Shorter answers could leave out important facts or be cut off. I check this with the same key-fact check and judge as for retrieval tuning, and by counting the answers that stopped because of the token limit. <!-- suggested: you answered "I don't know", edit in your own words -->

### Decision rule (written before running the experiment) <!-- new -->
A change is accepted when tokens drop by at least 30% and at most one of the 12 test questions gets worse.


## C. Experiment

### Setup
Agent: a small question answering agent over 7 pages of the official Python 3.14 documentation (newer than the model's training data). Baseline: chunks of 300 words, top-8 passages, normal instructions. Variant A: retrieval tuning (100-word chunks, top-4, chosen on 8 dev questions). Variant B: output control (answer in at most two sentences, max_tokens 300). Variant A+B: both. Retrieval is TF-IDF with cosine similarity (not embeddings, to keep it simple and fast). Answer model: openai/gpt-oss-20b on Groq, judge: qwen/qwen3.8-27b (a different model family). 20 questions: 8 dev (used to choose settings) and 12 test (used for the results), including 3 multi-passage and 3 unanswerable ones.

### What I measured
Prompt, completion and total tokens from the API usage numbers, retrieval hit rate (is the evidence in the retrieved text), answer correctness (key-fact rule check and the judge), answers cut off, latency. Decision rule written before the run: accept when tokens drop at least 30% and at most 1 of 12 questions gets worse.

### Results (12 test questions, one run each)
| variant | avg total tokens | vs baseline | avg output tokens | hit rate | correct (judge) |
|---|---|---|---|---|---|
| baseline | 3380 | 0% | 84 | 10/10 | 12/12 |
| A retrieval | 720 | -79% | 77 | 9/10 | 11/12 |
| B output | 3368 | -0.4% | 59 | 10/10 | 12/12 |
| A+B | 714 | -79% | 59 | 9/10 | 11/12 |

No answer was cut off. Latency went from 0.6 s to 0.3 s with A.

### Lessons learned
- About 97% of the tokens are input, so retrieval tuning matters much more than output control. B cut output tokens by about 30%, but total tokens barely changed. By my rule A and A+B pass (at the limit) and B fails on total tokens. B could still matter for cost, since output tokens are usually priced higher, but I did not measure cost.
- The one answer A lost (a question needing two passages) happened because one passage was not retrieved and the model gave a wrong answer instead of saying it did not know.
- The similarity threshold had no effect on this data.
- Without the documents the model made up answers on unanswerable questions, and two questions (t1, t2) were already known to it, so I checked this before trusting the results.
- My first rule check was too strict ("8 %" vs "8%", different "not in the documents" wordings). The judge was right each time, so I fixed the rule check and it now agrees with the judge on all 48 answers.
- Reasoning tokens count as output, so a "be concise" instruction does not remove them.

### Limits
12 test questions and one run each, so a difference of one question is not strong evidence. Settings for A were chosen on only 7 answerable dev questions. TF-IDF instead of embeddings. One answer model. The judge is a model too. The documentation was fetched with an AI-assisted tool.

## D. References
- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.
- Liu et al. (2023). Lost in the Middle: How Language Models Use Long Contexts.
- Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.
- Groq API documentation (usage fields, rate limits, reasoning_effort), console.groq.com/docs.
- Python 3.14 documentation, docs.python.org/3.14 (the 7 pages in data/docs).
