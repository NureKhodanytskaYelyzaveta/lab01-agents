from agent.environment import NOT_FOUND, lookup_event_function


def test_existing_function():
    assert lookup_event_function("Awake").startswith("awake:")


def test_name_is_normalized():
    assert lookup_event_function("  On Enable() ").startswith("onenable:")


def test_unknown_function():
    assert lookup_event_function("OnLateEnable").startswith(NOT_FOUND)
