import pytest

from agent.errors import DecisionError
from agent.validator import validate_decision


def test_valid_lookup():
    validate_decision({"action": "lookup_event_function", "arguments": {"name": "awake"}})


@pytest.mark.parametrize("decision", [
    {"action": "delete_files", "arguments": {}},                         # дії немає у whitelist
    {"action": "lookup_event_function", "arguments": {}},                # бракує аргументу
    {"action": "lookup_event_function", "arguments": {"name": 42}},      # хибний тип
    {"action": "finish"},                                                # немає arguments
])
def test_invalid_decisions(decision):
    with pytest.raises(DecisionError):
        validate_decision(decision)