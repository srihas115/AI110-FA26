# 💭 Reflection: Game Glitch Investigator

## 1. What was broken when you started?

The first run showed a number-guessing game, but its feedback could not be
trusted. A guess above the secret was labeled `Too High` while the message told
me to go higher, and a guess below the secret told me to go lower. Every even
attempt also converted the numeric secret to text before comparing it, which
could make a correct guess fail or compare values as strings. Attempts began at
one and were incremented before validation, so the displayed count was off and
even blank or invalid input consumed a turn.

**Bug Reproduction Log**

| Input / Trigger | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|---|---|---|---|---|
| Guess `60` when the secret is `50` | Show `Too High` and tell the player to guess lower | Outcome is `Too High`, but the hint says `Go HIGHER!` | None | `app.py`, `check_guess` |
| Enter the correct guess on an even-numbered attempt | End the game with a win | The secret is converted to a string, so the integer guess does not equal it | A `TypeError` is caught and the guess is treated as incorrect | `app.py`, submit block and `check_guess` |
| Submit an empty string or `abc` | Show a validation message without using an attempt | The attempt counter increases and the invalid value is added to history | `Enter a guess.` or `That is not a number.` | `app.py`, submit block |
| Press New Game after winning or losing | Reset the full game using the selected difficulty | Only attempts and secret reset; status, score, and history remain, and the range is always 1–100 | Game immediately remains stopped when status is `won` or `lost` | `app.py`, `if new_game` block |

---

## 2. How did you use AI as a teammate?

To be completed during the repair phase.

---

## 3. Debugging and testing your fixes

To be completed after the automated and manual verification steps.

---

## 4. What did you learn about Streamlit and state?

To be completed after the repair.

---

## 5. Looking ahead: your developer habits

To be completed after the repair.
