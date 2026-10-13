"""Automated verification for the repaired game rules."""

import pytest

from logic_utils import (
    check_guess,
    get_attempt_limit,
    get_outcome_message,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


@pytest.mark.parametrize(
    ("guess", "secret", "expected"),
    [
        (50, 50, "Win"),
        (60, 50, "Too High"),
        (40, 50, "Too Low"),
    ],
)
def test_check_guess(guess, secret, expected):
    assert check_guess(guess, secret) == expected


def test_directional_messages_match_outcomes():
    assert "lower" in get_outcome_message("Too High").lower()
    assert "higher" in get_outcome_message("Too Low").lower()


@pytest.mark.parametrize(
    ("difficulty", "expected_range", "expected_attempts"),
    [
        ("Easy", (1, 20), 6),
        ("Normal", (1, 100), 8),
        ("Hard", (1, 500), 5),
    ],
)
def test_difficulty_settings(difficulty, expected_range, expected_attempts):
    assert get_range_for_difficulty(difficulty) == expected_range
    assert get_attempt_limit(difficulty) == expected_attempts


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_blank_guess_is_rejected(raw):
    assert parse_guess(raw, 1, 100) == (False, None, "Enter a guess.")


@pytest.mark.parametrize("raw", ["abc", "4.2", "1e2"])
def test_non_integer_guess_is_rejected(raw):
    ok, value, error = parse_guess(raw, 1, 100)
    assert not ok
    assert value is None
    assert error == "Enter a whole number."


@pytest.mark.parametrize(
    ("raw", "expected_error"),
    [
        ("-1", "Guess must be at least 1."),
        ("1000000", "Guess must be at most 100."),
    ],
)
def test_out_of_range_guess_is_rejected(raw, expected_error):
    assert parse_guess(raw, 1, 100) == (False, None, expected_error)


def test_valid_guess_accepts_whitespace():
    assert parse_guess(" 42 ", 1, 100) == (True, 42, None)


@pytest.mark.parametrize("outcome", ["Too High", "Too Low"])
def test_wrong_guess_has_consistent_score_penalty(outcome):
    assert update_score(100, outcome, 1) == 90


def test_score_never_becomes_negative_and_win_has_no_penalty():
    assert update_score(5, "Too Low", 10) == 0
    assert update_score(70, "Win", 3) == 70
