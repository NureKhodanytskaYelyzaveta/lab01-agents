"""Оркестрація: цикл Observe -> Reason -> Validate -> Act -> Update -> Evaluate."""

import time
from collections.abc import Callable

from .environment import lookup_event_function
from .errors import ApiError, DecisionError
from .reasoning import get_decision
from .state import AgentState
from .validator import validate_decision

MAX_STEPS = 6

# Функцію рішень передають параметром: у тестах її замінює сценарій без LLM
DecideFn = Callable[[str, list[str], int, int], dict]


def execute_action(decision: dict, state: AgentState) -> str | None:
    """Dispatcher: перетворює перевірене рішення на виклик Python-функції."""
    action = decision["action"]
    args = decision["arguments"]
    if action == "lookup_event_function":
        return lookup_event_function(args["name"])
    if action == "finish":
        state.final_answer = args["answer"]
        state.finished = True
        state.stop_reason = "finish"
        return None
    raise DecisionError(f"no handler for action {action!r}")


def print_step(record: dict) -> None:
    print(f"\nSTEP {record['step']}")
    print(f"  ACTION:      {record['action']} {record['arguments'] or ''}")
    if record.get("decision_summary"):
        print(f"  DECISION:    {record['decision_summary']}")
    if record["observation"] is not None:
        print(f"  OBSERVATION: {record['observation']}")


def run_agent(goal: str, decide: DecideFn = get_decision,
              max_steps: int = MAX_STEPS) -> AgentState:
    state = AgentState(goal=goal)

    while not state.finished:
        # EVALUATE (бюджет): ліміт перевіряють до нового виклику LLM
        if state.step >= max_steps:
            state.finished = True
            state.stop_reason = "max_steps"
            state.final_answer = (
                f"Агент зупинився: вичерпано ліміт кроків ({max_steps}) "
                "без фінальної відповіді."
            )
            break

        state.step += 1
        record: dict = {"step": state.step}
        decision: dict | None = None
        started = time.perf_counter()
        try:
            state.llm_calls += 1                       # OBSERVE + REASON
            decision = decide(state.goal, state.observations, state.step, max_steps)
            validate_decision(decision)                # VALIDATE
            observation = execute_action(decision, state)   # ACT
            record.update(action=decision["action"],
                          arguments=decision["arguments"],
                          decision_summary=decision.get("decision_summary", ""))
        except ApiError as exc:
            observation = f"API_ERROR: {exc}"
            record.update(action="api_error", arguments=None, decision_summary="")
            state.finished = True
            state.stop_reason = "api_error"
            state.final_answer = "Агент зупинився: зовнішній API недоступний (див. трасування)."
        except DecisionError as exc:
            # Помилка стає спостереженням, і модель отримує шанс виправитися
            observation = f"ERROR: {exc}"
            record.update(action="rejected", arguments=None,
                          decision_summary="", rejected=decision)

        record["observation"] = observation
        record["seconds"] = round(time.perf_counter() - started, 2)
        state.trace.append(record)
        if observation is not None:
            state.observations.append(observation)     # UPDATE STATE
        print_step(record)

    return state