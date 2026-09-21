"""SAW: small, hand-checkable examples."""

import pytest

from backend.algorithms.saw import (
    calculate_saw_score,
    check_weights,
    normalize_all,
    normalize_benefit,
    normalize_cost,
)
from backend.services.carer_matching import CARER_WEIGHTS
from backend.services.shift_matching import SHIFT_WEIGHTS


def test_every_weight_set_sums_to_one():
    check_weights(CARER_WEIGHTS)
    check_weights(SHIFT_WEIGHTS)
    with pytest.raises(ValueError):
        check_weights({"a": 0.6, "b": 0.6})


def test_benefit_higher_is_better():
    assert normalize_benefit(30, 10, 50) == 0.5
    assert normalize_benefit(50, 10, 50) == 1.0


def test_cost_lower_is_better():
    assert normalize_cost(10, 10, 50) == 1.0
    assert normalize_cost(50, 10, 50) == 0.0


def test_equal_min_and_max_does_not_divide_by_zero():
    assert normalize_benefit(5, 5, 5) == 1.0
    assert normalize_cost(5, 5, 5) == 1.0
    assert normalize_all([7, 7, 7]) == [1.0, 1.0, 1.0]


def test_score_stays_between_zero_and_one():
    weights = {"a": 0.4, "b": 0.6}
    assert calculate_saw_score({"a": 0, "b": 0}, weights) == 0
    assert calculate_saw_score({"a": 1, "b": 1}, weights) == pytest.approx(1)


def test_better_criteria_give_a_better_score():
    weights = {"load": 0.5, "skill": 0.5}
    good = calculate_saw_score({"load": 0.9, "skill": 0.8}, weights)
    bad = calculate_saw_score({"load": 0.2, "skill": 0.3}, weights)
    assert good > bad


def test_known_manual_example():
    # care load 30 in [10, 50] (cost)    -> (50-30)/40 = 0.5
    # hours 20 in [10, 20] (cost)        -> (20-20)/10 = 0
    # skill 0.9 in [0.7, 1.0] (benefit)  -> (0.9-0.7)/0.3 = 2/3
    weights = {"care_load": 0.4, "weekly_hours": 0.2, "skill": 0.4}
    normalised = {
        "care_load": normalize_cost(30, 10, 50),
        "weekly_hours": normalize_cost(20, 10, 20),
        "skill": normalize_benefit(0.9, 0.7, 1.0),
    }
    assert calculate_saw_score(normalised, weights) == pytest.approx(0.4 * 0.5 + 0.2 * 0 + 0.4 * 2 / 3)
