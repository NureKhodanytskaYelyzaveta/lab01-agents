# manual-agent

Мінімальний AI-агент без фреймворку: цикл Observe → Reason → Validate → Act → Update → Evaluate.
Предметна область: життєвий цикл MonoBehaviour в Unity.

## Модулі

- `agent/environment.py`: середовище (8 об'єктів, `lookup_event_function`, `NOT_FOUND`).
- `agent/state.py`: `AgentState`.
- `agent/reasoning.py`: спостереження, інструкція, рішення через Gemini API.
- `agent/validator.py`: білий список дій і перевірка аргументів.
- `agent/loop.py`: цикл, диспетчер, `MAX_STEPS`, обробка помилок.
- `main.py`: запуск агента (`--mode oneshot` для базової лінії), запис трас у `traces/`.

## Запуск

```bash
cp .env.example .env        # вписати GEMINI_API_KEY
uv run python main.py "Порівняй Awake, OnEnable і Start"
uv run python main.py "Порівняй Awake, OnEnable і Start" --mode oneshot
uv run pytest -q
```