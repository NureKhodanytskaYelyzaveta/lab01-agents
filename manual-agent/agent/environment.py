"""Середовище агента: життєвий цикл MonoBehaviour в Unity (event functions).

Детермінований код без LLM. Джерела фактів: Unity Manual,
"Order of execution for event functions"; Unity Scripting API,
клас MonoBehaviour.
"""

EVENT_FUNCTIONS: dict[str, str] = {
    "awake": (
        "Awake викликається один раз, коли завантажується екземпляр скрипта, "
        "ще до Start. Він виконується, навіть якщо компонент вимкнений, "
        "але лише коли GameObject активний."
    ),
    "onenable": (
        "OnEnable викликається щоразу, коли компонент стає увімкненим і "
        "активним. Під час першого завантаження він іде після Awake."
    ),
    "start": (
        "Start викликається один раз перед першим кадром, у якому виконується "
        "Update, і лише якщо компонент увімкнений. Він іде після Awake."
    ),
    "fixedupdate": (
        "FixedUpdate викликається з фіксованим кроком часу незалежно від "
        "частоти кадрів і призначений для фізичних розрахунків. За один кадр "
        "він може виконатися кілька разів або жодного."
    ),
    "update": (
        "Update викликається один раз на кожен кадр, якщо компонент увімкнений. "
        "У ньому зазвичай обробляють ввід і ігрову логіку."
    ),
    "lateupdate": (
        "LateUpdate викликається один раз на кадр після того, як виконано "
        "всі виклики Update. Його часто використовують для камери, що "
        "стежить за об'єктом."
    ),
    "ondisable": (
        "OnDisable викликається, коли компонент вимикається або GameObject "
        "стає неактивним. Він також викликається перед знищенням об'єкта."
    ),
    "ondestroy": (
        "OnDestroy викликається, коли MonoBehaviour знищується, наприклад "
        "після Destroy або під час вивантаження сцени. Він викликається лише "
        "для об'єктів, які раніше були активними."
    ),
}

NOT_FOUND = "NOT_FOUND"


def normalize_name(name: str) -> str:
    """Зводить ' On Enable() ', 'on_enable', 'ONENABLE' до ключа 'onenable'."""
    cleaned = name.strip().lower().removesuffix("()")
    for ch in (" ", "-", "_"):
        cleaned = cleaned.replace(ch, "")
    return cleaned


def lookup_event_function(name: str) -> str:
    """Return verified information about one Unity MonoBehaviour event function.

    Use it when the user asks about a specific lifecycle method such as
    Awake, OnEnable, Start, FixedUpdate, Update, LateUpdate, OnDisable
    or OnDestroy.

    Args:
        name: name of the method, for example "Awake" or "FixedUpdate".

    Returns:
        "<id>: <description>" or a line starting with NOT_FOUND.
    """
    key = normalize_name(name)
    if key not in EVENT_FUNCTIONS:
        return f"{NOT_FOUND}: no verified information about '{name}'."
    return f"{key}: {EVENT_FUNCTIONS[key]}"


# Фази життєвого циклу за Unity Manual, "Order of execution for event functions"
PHASES: dict[str, tuple[str, ...]] = {
    "initialization": ("Awake", "OnEnable", "Start"),
    "physics": ("FixedUpdate",),
    "game_logic": ("Update", "LateUpdate"),
    "decommissioning": ("OnDisable", "OnDestroy"),
}


def list_events_by_phase(phase: str) -> str:
    """Return verified list of MonoBehaviour event functions in one lifecycle phase.

    Use it when the user asks which event functions belong to a phase.
    Known phases: initialization, physics, game_logic, decommissioning.

    Args:
        phase: name of the phase, for example "initialization".

    Returns:
        "<phase>: <function>, <function>" or a line starting with NOT_FOUND.
    """
    key = phase.strip().lower().replace(" ", "_").replace("-", "_")
    if key not in PHASES:
        known = ", ".join(PHASES)
        return f"{NOT_FOUND}: no verified phase '{phase}'. Known phases: {known}."
    return f"{key}: {', '.join(PHASES[key])}"
