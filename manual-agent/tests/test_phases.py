import pytest

from agent.environment import NOT_FOUND, list_events_by_phase
from agent.errors import DecisionError
from agent.loop import run_agent
from agent.validator import validate_decision


def test_known_phase():
    assert list_events_by_phase("Initialization") == "initialization: Awake, OnEnable, Start"


def test_phase_name_is_normalized():
    assert list_events_by_phase(" Game Logic ").startswith("game_logic:")


def test_unknown_phase():
    assert list_events_by_phase("rendering").startswith(NOT_FOUND)


def test_validator_accepts_phase_action():
    validate_decision({"action": "list_events_by_phase", "arguments": {"phase": "physics"}})


def test_validator_requires_phase_argument():
    with pytest.raises(DecisionError):
        validate_decision({"action": "list_events_by_phase", "arguments": {}})


def test_second_action_is_dispatched():
    script = iter([
        {"action": "list_events_by_phase", "arguments": {"phase": "physics"}},
        {"action": "finish", "arguments": {"answer": "ok"}},
    ])
    state = run_agent("Тест", decide=lambda goal, obs, step, max_steps: next(script))
    assert state.observations[0] == "physics: FixedUpdate"
    assert state.stop_reason == "finish"
