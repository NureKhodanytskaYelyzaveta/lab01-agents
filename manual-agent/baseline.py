"""Базова лінія: один виклик LLM без циклу, дій і середовища."""

from agent.reasoning import MODEL, get_client


def one_shot_answer(goal: str) -> str:
    response = get_client().models.generate_content(model=MODEL, contents=goal)
    return response.text