"""Тести циклу без звернень до API: рішення моделі підміняє сценарій."""

from agent.errors import ApiError
from agent.loop import run_agent

def scripted(decisions):
    queue = iter(decisions)

    def decide(goal, observations, step, max_steps):
        return next(queue)

    return decide


def test_lookup_then_finish():
    decide = scripted([
        {"action": "lookup_event_function", "arguments": {"name": "update"},
         "decision_summary": "Потрібні дані про Update."},
        {"action": "finish", "arguments": {"answer": "Update викликається щокадру."},
         "decision_summary": "Даних достатньо."},
    ])
    state = run_agent("Що таке Update?", decide=decide)
    assert state.stop_reason == "finish"
    assert state.llm_calls == 2
    assert state.observations[0].startswith("update:")


def test_stops_at_max_steps():
    def endless(goal, observations, step, max_steps):
        return {"action": "lookup_event_function", "arguments": {"name": "awake"}}

    state = run_agent("Зациклитися", decide=endless, max_steps=3)
    assert state.stop_reason == "max_steps"
    assert state.step == 3


def test_invalid_action_becomes_observation():
    decide = scripted([
        {"action": "rm_rf", "arguments": {}},
        {"action": "finish", "arguments": {"answer": "ok"}},
    ])
    state = run_agent("Тест", decide=decide)
    assert state.observations[0].startswith("ERROR: unknown action")
    assert state.stop_reason == "finish"

def test_api_error_stops_agent_and_keeps_trace():
    def broken(goal, observations, step, max_steps):
        raise ApiError("503 UNAVAILABLE")

    state = run_agent("Тест", decide=broken)
    assert state.stop_reason == "api_error"
    assert len(state.trace) == 1