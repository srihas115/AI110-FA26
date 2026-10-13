"""Pure game rules for Project 1: Game Glitch Investigator."""

from typing import Optional


DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    "Hard": (1, 500),
}

ATTEMPT_LIMITS = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}

OUTCOME_MESSAGES = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Too high — guess lower!",
    "Too Low": "📈 Too low — guess higher!",
}


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive number range for a difficulty level."""
    return DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["Normal"])


def get_attempt_limit(difficulty: str) -> int:
    """Return the number of valid guesses allowed for a difficulty level."""
    return ATTEMPT_LIMITS.get(difficulty, ATTEMPT_LIMITS["Normal"])


def parse_guess(
    raw: Optional[str],
    low: Optional[int] = None,
    high: Optional[int] = None,
) -> tuple[bool, Optional[int], Optional[str]]:
    """Validate text input and return an integer guess plus an error, if any."""
    if raw is None or not raw.strip():
        return False, None, "Enter a guess."

    try:
        value = int(raw.strip())
    except (TypeError, ValueError):
        return False, None, "Enter a whole number."

    if low is not None and value < low:
        return False, None, f"Guess must be at least {low}."
    if high is not None and value > high:
        return False, None, f"Guess must be at most {high}."

    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """Compare two integers and return Win, Too High, or Too Low."""
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def get_outcome_message(outcome: str) -> str:
    """Return player-facing guidance for a comparison outcome."""
    return OUTCOME_MESSAGES.get(outcome, "Try another guess.")


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Deduct ten points for a wrong valid guess, never dropping below zero."""
    del attempt_number  # Kept in the public API so starter callers remain compatible.
    if outcome in {"Too High", "Too Low"}:
        return max(0, current_score - 10)
    return current_score
