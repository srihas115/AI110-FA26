# Project 1 AI Interactions Log

## Agent Workflow

**What task did you give the agent?**

I asked OpenAI Codex to inspect the CodePath Project 1 assignment from Week 3
and its official starter, reproduce the bugs from the code, repair the
Streamlit game, add automated tests, complete the documentation, and make
phase-based Git commits.

**What did the agent do?**

- Added the official starter structure under `Project 1/game-glitch-investigator`.
- Connected four visible symptoms to their code-level causes.
- Moved game rules from `app.py` into `logic_utils.py`.
- Repaired comparison, validation, scoring, difficulty, and reset behavior.
- Expanded `tests/test_game_logic.py` and ran the full suite.
- Completed the README, reflection, and test evidence in separate commits.

**What did you have to verify or fix manually?**

I reviewed the proposed separation between outcomes and UI messages against the
starter test contract. I kept `check_guess` returning a single outcome instead
of accepting a tuple-returning version, because the smaller API is easier to
test and matches the starter expectations. Verification included reading the
diff, running pytest, compiling both Python modules, and loading the Streamlit
app with its testing API.

## Test Generation

Prompt used: “Generate focused pytest cases for `parse_guess` that cover blank,
non-numeric, decimal, negative, extremely large, and whitespace-padded input.
Also test that invalid inputs return useful errors without reaching game logic.”

| Edge Case | AI-Suggested Test | Did It Pass? | Why It Was Chosen |
|---|---|---|---|
| Negative number (`-1`) | Assert it is rejected below the active lower bound | Yes | Prevents guesses outside the selected difficulty range |
| Decimal (`4.2`) | Assert whole-number validation fails cleanly | Yes | Prevents silent truncation from turning `4.2` into `4` |
| Extremely large value (`1000000`) | Assert it is rejected above the active upper bound | Yes | Confirms range validation works on oversized numeric input |
| Blank/whitespace input | Parameterize `None`, empty text, and spaces | Yes | Confirms an empty submission does not become an attempt |
| Padded integer (` 42 `) | Assert surrounding whitespace is accepted | Yes | Keeps common, harmless input formatting user-friendly |

## Verification Output

```text
...................                                                      [100%]
19 passed in 0.01s
```
