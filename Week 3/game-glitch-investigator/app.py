"""Streamlit interface for the repaired number-guessing game."""

import random

import streamlit as st

from logic_utils import (
    check_guess,
    get_attempt_limit,
    get_outcome_message,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


def reset_game(difficulty: str) -> None:
    """Create a clean game in Streamlit session state."""
    low, high = get_range_for_difficulty(difficulty)
    # FIX: Codex helped consolidate every state reset so a finished game can restart.
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 100
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.active_difficulty = difficulty


st.set_page_config(page_title="Game Glitch Investigator", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("A repaired number-guessing game with testable core logic.")

st.sidebar.header("Settings")
difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

low, high = get_range_for_difficulty(difficulty)
attempt_limit = get_attempt_limit(difficulty)

if "secret" not in st.session_state:
    reset_game(difficulty)
elif st.session_state.get("active_difficulty") != difficulty:
    reset_game(difficulty)
    st.toast(f"Started a new {difficulty.lower()} game.")

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
st.sidebar.metric("Score", st.session_state.score)

st.subheader("Make a guess")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    f"Enter a whole number from {low} to {high}:",
    key=f"guess_input_{difficulty}",
    disabled=st.session_state.status != "playing",
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button(
        "Submit Guess 🚀",
        disabled=st.session_state.status != "playing",
    )
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    reset_game(difficulty)
    st.rerun()

if submit:
    ok, guess, error = parse_guess(raw_guess, low, high)

    if not ok:
        st.error(error)
    else:
        # FIX: Validate first, keep the secret numeric, then count exactly one attempt.
        st.session_state.attempts += 1
        st.session_state.history.append(guess)
        outcome = check_guess(guess, st.session_state.secret)
        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.session_state.status = "won"
            st.balloons()
            st.success(
                f"You won in {st.session_state.attempts} guesses! "
                f"Final score: {st.session_state.score}"
            )
        else:
            if show_hint:
                st.warning(get_outcome_message(outcome))

            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )

attempts_left = max(0, attempt_limit - st.session_state.attempts)
st.info(
    f"Range: {low}–{high} · Attempts left: {attempts_left} · "
    f"Score: {st.session_state.score}"
)

if st.session_state.status == "won" and not submit:
    st.success("You won! Start a new game to play again.")
elif st.session_state.status == "lost" and not submit:
    st.error("Game over. Start a new game to try again.")

if st.session_state.history:
    st.write("Guess history:", ", ".join(map(str, st.session_state.history)))

st.divider()
st.caption("Core rules live in logic_utils.py and are verified with pytest.")
