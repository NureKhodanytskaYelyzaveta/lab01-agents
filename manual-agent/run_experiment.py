"""Запуск запитів A-E на one-shot і власному агенті; результати в experiments/."""
import argparse
import json
import time
from pathlib import Path

from agent.loop import run_agent
from baseline import one_shot_answer
from main import save_trace

QUERIES = {
    "A": "Розкажи про FixedUpdate",
    "B": "Порівняй Awake і Start",
    "C": "Порівняй Awake, OnEnable і Start",
    "D": "Опиши OnTriggerEnter",
    "E": "Що таке життєвий цикл MonoBehaviour?",
}

parser = argparse.ArgumentParser()
parser.add_argument("--types", default="ABCDE", help="наприклад AB або D")
parser.add_argument("--repeats", type=int, default=1)
parser.add_argument("--pause", type=int, default=5, help="пауза між запусками, с")
args = parser.parse_args()

Path("experiments").mkdir(exist_ok=True)
results = []

for qtype in args.types:
    goal = QUERIES[qtype]
    for run in range(1, args.repeats + 1):
        # one-shot
        started = time.perf_counter()
        try:
            answer, error = one_shot_answer(goal), None
        except Exception as exc:  # фіксуємо відмову API, не ховаємо її
            answer, error = None, f"{type(exc).__name__}: {exc}"[:200]
        results.append({"type": qtype, "system": "one-shot", "run": run,
                        "goal": goal, "llm_calls": 1, "actions": 0,
                        "seconds": round(time.perf_counter() - started, 2),
                        "stop": "error" if error else "answer",
                        "error": error, "answer": answer})
        time.sleep(args.pause)

        # власний агент
        started = time.perf_counter()
        try:
            state = run_agent(goal)
            trace_file = save_trace(state)
            actions = sum(1 for r in state.trace
                          if r.get("action") == "lookup_event_function")
            results.append({"type": qtype, "system": "manual-agent", "run": run,
                            "goal": goal, "llm_calls": state.llm_calls,
                            "steps": state.step, "actions": actions,
                            "seconds": round(time.perf_counter() - started, 2),
                            "stop": state.stop_reason, "error": None,
                            "trace": str(trace_file), "answer": state.final_answer})
        except Exception as exc:
            results.append({"type": qtype, "system": "manual-agent", "run": run,
                            "goal": goal, "seconds": round(time.perf_counter() - started, 2),
                            "stop": "error", "error": f"{type(exc).__name__}: {exc}"[:200]})
        time.sleep(args.pause)

out = Path("experiments") / f"results_{time.strftime('%Y%m%d_%H%M%S')}.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

print("\ntype | system       | run | LLM | actions | seconds | stop")
for r in results:
    print(f"{r['type']:4} | {r['system']:12} | {r['run']:3} | {r.get('llm_calls','-'):>3} | "
          f"{r.get('actions','-'):>7} | {r['seconds']:>7} | {r['stop']}")
print(f"\nsaved: {out}")
