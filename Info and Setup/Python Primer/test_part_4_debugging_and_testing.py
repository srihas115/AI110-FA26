"""Tests for the Python Primer Part 4 debugging mini-challenge."""

import runpy
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).with_name("part 4 debugging and testing.py")
LESSON = runpy.run_path(MODULE_PATH)

add = LESSON["add"]
multiply = LESSON["multiply"]
sixth_item = LESSON["sixth_item"]


def test_sixth_item_uses_zero_based_indexing():
    assert sixth_item([1, 2, 3, 4, 5, 6]) == 6


def test_sixth_item_reports_a_short_list():
    with pytest.raises(IndexError):
        sixth_item([1, 2, 3])


def test_add():
    assert add(1, 3) == 4


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (3, 4, 12),
        (0, 99, 0),
        (-3, 4, -12),
        (-3, -4, 12),
        (2.5, 4, 10.0),
    ],
)
def test_multiply_handles_normal_and_edge_cases(a, b, expected):
    assert multiply(a, b) == expected
