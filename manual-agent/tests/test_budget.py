from agent.errors import ApiError
from agent.loop import run_agent

LOOKUP = {"action": "lookup_event_function", "arguments": {"name": "awake"}}


def test_max_llm_calls_stops_agent():
    state = run_agent("Зациклитися", decide=lambda g, o, s, m: dict(LOOKUP),
                      max_steps=10, max_llm_calls=3)
    assert state.stop_reason == "max_llm_calls"
    assert state.llm_calls == 3
    assert state.step == 3


def test_retries_count_towards_llm_budget():
    def with_retries(goal, observations, step, max_steps):
        return {**LOOKUP, "_requests": 3}

    state = run_agent("Тест", decide=with_retries, max_steps=10, max_llm_calls=5)
    assert state.stop_reason == "max_llm_calls"
    assert state.llm_calls == 6          # крок 1: 3 запити, крок 2: ще 3


def test_api_error_attempts_count_towards_budget():
    def broken(goal, observations, step, max_steps):
        exc = ApiError("429 after 4 attempt(s)")
        exc.attempts = 4
        raise exc

    state = run_agent("Тест", decide=broken)
    assert state.stop_reason == "api_error"
    assert state.llm_calls == 4
