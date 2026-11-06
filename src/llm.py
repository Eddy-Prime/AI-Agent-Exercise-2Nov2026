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


def ask(messages, model, max_tokens=None, temp=0):
    # API parameters
    options = {
        "model": model,
        "messages": messages,
        "temperature": temp,
    }

    # Limit the number of tokens if provided
    if max_tokens is not None:
        options["max_tokens"] = max_tokens

    key_source = json.dumps(
        {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temp,
        },
        sort_keys=True,
    )
    key = hashlib.sha256(key_source.encode()).hexdigest()
    path = CACHE_DIR / f"{key}.json"

    if path.exists():
        result = json.loads(path.read_text())
        result["cached"] = True
        return result

    for attempt in range(4):
        try:
            start = time.perf_counter()
            response = client.chat.completions.create(**options) # Send the request to the AI
            # Calc' how long the response took
            latency = time.perf_counter() - start
            break
        except RateLimitError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)   # waits 1s, 2s, 4s

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
    print(ask(msgs, MODEL, max_tokens=300))
    print(ask(msgs, MODEL, max_tokens=300))
