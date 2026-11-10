# lab01-agents

Лабораторна робота №1: побудова AI-агента з власним циклом
Observe → Reason → Act → Evaluate та реалізація на Google ADK.

Предметна область: життєвий цикл MonoBehaviour в Unity (event functions).
Модель для всіх систем: gemini-3.6-flash.

## Структура

- `manual-agent/`: власний агент без фреймворку (цикл, стан, валідатор, трасування).
- `adk-agent/`: той самий агент на Google ADK з інструментом `lookup_event_function`.
- `manual-agent/experiment.md`: методика й таблиця експерименту (one-shot, власний агент, ADK).

## Запуск

```bash
# власний агент
cd manual-agent
cp .env.example .env        # вписати GEMINI_API_KEY
uv run python main.py "Порівняй Awake, OnEnable і Start"
uv run python main.py "Порівняй Awake, OnEnable і Start" --mode oneshot
uv run pytest -q

# ADK-агент
cd ../adk-agent
agents-cli playground
agents-cli run "Порівняй Awake, OnEnable і Start"
```

Файл `.env` у репозиторій не комітиться.