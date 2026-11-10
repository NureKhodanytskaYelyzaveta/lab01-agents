import argparse
import json
import time
from pathlib import Path

from agent.loop import run_agent
from baseline import one_shot_answer


def save_trace(state) -> Path:
    Path("traces").mkdir(exist_ok=True)
    path = Path("traces") / f"trace_{time.strftime('%Y%m%d_%H%M%S')}.json"
    payload = {
        "goal": state.goal,
        "stop_reason": state.stop_reason,
        "steps": state.step,
        "llm_calls": state.llm_calls,
        "final_answer": state.final_answer,
        "trace": state.trace,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Мінімальний AI-агент (ЛР 1)")
    parser.add_argument("goal", help="мета агента в лапках")
    parser.add_argument("--mode", choices=["agent", "oneshot"], default="agent")
    args = parser.parse_args()

    started = time.perf_counter()
    if args.mode == "oneshot":
        print(one_shot_answer(args.goal))
        print(f"\n[one-shot] LLM calls: 1, time: {time.perf_counter() - started:.2f} s")
        return

    state = run_agent(args.goal)
    print("\nFINAL ANSWER:\n" + (state.final_answer or ""))
    print(f"\n[agent] steps: {state.step}, LLM calls: {state.llm_calls}, "
          f"stop: {state.stop_reason}, time: {time.perf_counter() - started:.2f} s")
    print(f"trace saved: {save_trace(state)}")


if __name__ == "__main__":
    main()