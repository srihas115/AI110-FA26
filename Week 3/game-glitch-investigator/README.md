# 🎮 Game Glitch Investigator

A repaired Streamlit number-guessing game built for CodePath AI110. The starter
intentionally mixed interface code with game rules and included broken hints,
unstable comparisons, inconsistent scoring, and incomplete session resets. The
finished project separates the rules into testable functions and keeps the UI
state predictable across Streamlit reruns.

## Features

- Easy, Normal, and Hard modes with matching ranges and attempt limits
- Correct higher/lower guidance
- Whole-number and active-range validation that does not consume invalid turns
- Stable secret numbers stored in Streamlit session state
- Consistent scoring, guess history, and complete new-game resets
- 19 automated tests, including input edge cases

## Setup and Run

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

Run the tests with:

```bash
python -m pytest -q
```

## What Was Fixed

The original hint text pointed in the opposite direction from the comparison
result. It also converted the secret to a string on every even attempt, counted
invalid input as a guess, started the attempt counter at one, and only partially
reset state for a new game. The repair moved the rules to `logic_utils.py`, kept
the secret numeric, validated before mutating state, and centralized the reset
flow. Scoring now begins at 100, deducts ten points consistently for either kind
of incorrect valid guess, and never becomes negative.

## Demo Walkthrough

1. The user selects Normal mode, which sets a range of 1–100 and allows eight valid guesses.
2. The user enters `40` when the secret is `50`; the game returns “Too low — guess higher!” and the score changes from 100 to 90.
3. The user enters `70`; the game returns “Too high — guess lower!” and the score changes to 80.
4. The user enters `4.2`; the game requests a whole number without changing attempts, history, or score.
5. The user enters `50`; the game reports a win, preserves the final score, and disables further guesses.
6. The user presses New Game; the secret, attempts, score, status, and history all reset for the selected difficulty.

## Test Results

```text
...................                                                      [100%]
19 passed in 0.01s
```

The Streamlit app was also loaded with `streamlit.testing.v1.AppTest`; it
rendered the title and initial game status with zero exceptions.

## Project Files

- `app.py` — Streamlit interface and session-state flow
- `logic_utils.py` — pure game rules and validation
- `tests/test_game_logic.py` — core and edge-case test suite
- `reflection.md` — bug log, AI critique, verification, and takeaways
- `ai_interactions.md` — optional advanced-testing and agent-workflow evidence
- `test_results.txt` — captured pytest output
