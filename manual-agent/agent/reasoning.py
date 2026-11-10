import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from .errors import ApiError, DecisionError

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

RETRY_CODES = {429, 500, 503, 504}
MAX_ATTEMPTS = 4

AGENT_INSTRUCTION = """
You are the decision component of a small educational AI agent about the
Unity MonoBehaviour lifecycle (event functions). You do not chat.
On every call you choose exactly one action.

Available actions:
1. lookup_event_function
   Use it when verified information about a MonoBehaviour event function
   is needed.
   Arguments: {"name": string}   e.g. "Awake", "OnEnable", "FixedUpdate"
2. finish
   Use it when the verified observations are enough to reach the goal,
   or when the environment reported that the information does not exist.
   Arguments: {"answer": string}   final answer in Ukrainian

Return valid JSON only:
{"action": "lookup_event_function | finish",
 "arguments": {...},
 "decision_summary": "one short sentence: why this action"}

Rules:
- Use only facts from VERIFIED OBSERVATIONS in the final answer.
- If an observation starts with NOT_FOUND, say the information is missing;
  do not invent it.
- If an observation starts with ERROR, fix your previous decision.
- Do not repeat a lookup that is already present in the observations.
- decision_summary is one sentence; do not reveal hidden chain-of-thought.
"""

_client: genai.Client | None = None


def get_client() -> genai.Client:
    """Лінива ініціалізація: тести без мережі імпортують модуль без ключа."""
    global _client
    if _client is None:
        _client = genai.Client()  # читає GEMINI_API_KEY з оточення
    return _client


def build_observation(goal: str, observations: list[str], step: int, max_steps: int) -> str:
    """OBSERVE: формує те, що бачить модель на поточному кроці."""
    known = "\n".join(f"- {item}" for item in observations) or "None yet."
    return (
        f"GOAL:\n{goal}\n\n"
        f"CURRENT STEP: {step} of {max_steps}\n\n"
        f"VERIFIED OBSERVATIONS:\n{known}\n\n"
        "AVAILABLE ACTIONS: lookup_event_function, finish\n"
        "Choose the next action."
    )


def parse_decision(text: str | None) -> dict:
    """Перетворює текст відповіді моделі на словник або піднімає DecisionError."""
    try:
        decision = json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise DecisionError(f"invalid JSON from model: {exc}") from exc
    if not isinstance(decision, dict):
        raise DecisionError("decision must be a JSON object")
    return decision


def get_decision(goal: str, observations: list[str], step: int, max_steps: int) -> dict:
    """REASON: один виклик LLM повертає одне структуроване рішення."""
    prompt = build_observation(goal, observations, step, max_steps)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = get_client().models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=AGENT_INSTRUCTION,
                    response_mime_type="application/json",
                ),
            )
            break
        except genai_errors.APIError as exc:
            if exc.code not in RETRY_CODES or attempt == MAX_ATTEMPTS:
                raise ApiError(f"{exc.code} after {attempt} attempt(s)") from exc
            time.sleep(2 * attempt)   # пауза 2, 4, 6 с
    return parse_decision(response.text)