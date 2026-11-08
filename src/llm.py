import hashlib
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq, RateLimitError

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CACHE_DIR = Path(__file__).parent.parent / "results" / "cache"

# Groq free plan: about 8K tokens per minute per model. We stay a bit under it.
TOKENS_PER_MINUTE = 7000
_recent_calls = []  # (time, tokens) of the API calls made in the last minute


def _wait_for_token_budget(expected_tokens):
    # Sleep until the last minute of API calls leaves room for this call
    while True:
        now = time.time()
        _recent_calls[:] = [(t, n) for t, n in _recent_calls if now - t < 60]
        used = sum(n for _, n in _recent_calls)
        if not _recent_calls or used + expected_tokens <= TOKENS_PER_MINUTE:
            return
        time.sleep(max(1, 61 - (now - _recent_calls[0][0])))


def ask(messages, model, max_tokens=None, temp=0, reasoning_effort=None):
    # API parameters
    options = {
        "model": model,
        "messages": messages,
        "temperature": temp,
    }

    # Limit the number of tokens if provided
    if max_tokens is not None:
        options["max_tokens"] = max_tokens

    # Reasoning effort (only for models that support it)
    if reasoning_effort is not None:
        options["reasoning_effort"] = reasoning_effort

    key_source = json.dumps(
        {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temp,
            "reasoning_effort": reasoning_effort,
        },
        sort_keys=True,
    )
    key = hashlib.sha256(key_source.encode()).hexdigest()
    path = CACHE_DIR / f"{key}.json"

    if path.exists():
        result = json.loads(path.read_text())
        result["cached"] = True
        return result

    # Rough guess of the tokens this call will use (about 4 characters per token)
    _wait_for_token_budget(len(json.dumps(messages)) // 4 + (max_tokens or 400))

    for attempt in range(4):
        try:
            start = time.perf_counter()
            response = client.chat.completions.create(**options) # Send the request to the AI
            # Calc' how long the response took
            latency = time.perf_counter() - start
            _recent_calls.append((time.time(), response.usage.total_tokens))
            break
        except RateLimitError:
            if attempt == 3:
                raise
            time.sleep(20 * (attempt + 1))   # waits 20s, 40s, 60s

    # store de results in a dictionary
    result = {
        "text": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "latency_s": latency,
        "finish_reason": response.choices[0].finish_reason,
        "cached": False,
    }

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result))
    return result


if __name__ == "__main__":
    MODEL = "openai/gpt-oss-20b"
    msgs = [{"role": "user", "content": "What is 2+2?"}]
    print(ask(msgs, MODEL, max_tokens=300, reasoning_effort="low"))
    print(ask(msgs, MODEL, max_tokens=300, reasoning_effort="low"))
