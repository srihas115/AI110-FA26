# 💭 Project 1 Reflection: Game Glitch Investigator

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

I used OpenAI Codex to trace the relationship between the Streamlit event flow
in `app.py` and the pure functions planned for `logic_utils.py`. Its useful
suggestion was to validate input before incrementing the attempt counter; I
accepted that change and verified it with parameterized tests for blank,
non-numeric, decimal, negative, and oversized input. I did not accept the idea
of keeping `check_guess` as a tuple-returning UI helper because the starter
tests expected a single outcome string and mixing messages with comparison
logic made the function harder to reuse. Instead, I separated
`check_guess` from `get_outcome_message` and verified both independently.

---

## 3. Debugging and testing your fixes

I treated a bug as fixed only when the code-level cause was removed and a test
captured the expected behavior. The main parameterized comparison test checks
winning, too-high, and too-low guesses, while a second test checks that each
outcome points in the correct direction. Codex helped enumerate edge cases for
`parse_guess`; those cases showed that decimal text, blank input, values outside
the active range, and very large values now fail cleanly without entering the
game logic. I also checked that wrong guesses use the same score penalty and
that the score cannot become negative.

---

## 4. What did you learn about Streamlit and state?

Streamlit reruns the Python file from top to bottom whenever a widget causes an
interaction, so ordinary local variables should not be treated as durable game
state. `st.session_state` acts like a per-user backpack that survives those
reruns and stores the secret, attempts, score, status, and history. I also
learned that related state must reset together; changing only the secret and
attempt count can leave a supposedly new game stuck in an old won or lost
status.

---

## 5. Looking ahead: your developer habits

I want to keep reproducing bugs in a small table before changing code, because
the trigger, symptom, and suspected location made each fix easier to verify. I
also want to keep pure logic outside framework files so automated tests do not
need to simulate the full interface. Next time I work with AI, I will state the
existing API contract and success tests earlier so the first proposal stays
within scope. This project changed my view of AI-generated code: a plausible
implementation is a draft that still needs human review, focused tests, and
verification against actual behavior.
