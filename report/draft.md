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
1. Why I chose it:
2. How I would implement / evaluate it:
3. Metrics:
4. How I check that quality did not drop:

### Technique 2: Output control
1. Why I chose it:
2. How I would implement / evaluate it:
3. Metrics:
4. How I check that quality did not drop:
