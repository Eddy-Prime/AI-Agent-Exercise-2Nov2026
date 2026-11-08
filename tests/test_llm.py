import types

import llm


def fake_response(text="4"):
    usage = types.SimpleNamespace(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    choice = types.SimpleNamespace(message=types.SimpleNamespace(content=text), finish_reason="stop")
    return types.SimpleNamespace(choices=[choice], usage=usage)


class FakeClient:
    def __init__(self):
        self.calls = 0
        self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        return fake_response()


def setup(monkeypatch, tmp_path):
    fake = FakeClient()
    monkeypatch.setattr(llm, "client", fake)
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path)
    return fake


MSGS = [{"role": "user", "content": "What is 2+2?"}]


def test_second_identical_call_comes_from_cache(monkeypatch, tmp_path):
    fake = setup(monkeypatch, tmp_path)
    first = llm.ask(MSGS, "m", max_tokens=50)
    second = llm.ask(MSGS, "m", max_tokens=50)
    assert fake.calls == 1
    assert first["cached"] is False and second["cached"] is True
    assert first["total_tokens"] == second["total_tokens"] == 15


def test_token_counts_come_from_the_api_usage(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    r = llm.ask(MSGS, "m")
    assert (r["prompt_tokens"], r["completion_tokens"], r["total_tokens"]) == (10, 5, 15)
    assert r["finish_reason"] == "stop"


def test_cache_key_depends_on_max_tokens_and_reasoning_effort(monkeypatch, tmp_path):
    fake = setup(monkeypatch, tmp_path)
    llm.ask(MSGS, "m", max_tokens=50)
    llm.ask(MSGS, "m", max_tokens=100)
    llm.ask(MSGS, "m", max_tokens=50, reasoning_effort="low")
    assert fake.calls == 3


def test_optional_parameters_are_sent_only_when_set(monkeypatch, tmp_path):
    fake = setup(monkeypatch, tmp_path)
    llm.ask(MSGS, "m")
    assert "max_tokens" not in fake.last_kwargs and "reasoning_effort" not in fake.last_kwargs
    llm.ask(MSGS, "m", max_tokens=7, reasoning_effort="low")
    assert fake.last_kwargs["max_tokens"] == 7 and fake.last_kwargs["reasoning_effort"] == "low"
