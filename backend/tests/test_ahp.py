import pytest

from backend.algorithms.ahp import (
    CONSISTENCY_THRESHOLD,
    RANDOM_CONSISTENCY_INDEX,
    build_matrix,
    derive_weights,
    geometric_mean_weights,
    principal_eigenvector,
)
from backend.config.risk_weights import (
    JUDGEMENTS,
    RISK_CRITERIA,
    RISK_WEIGHT_MODEL,
    RISK_WEIGHTS,
)


def test_reproduces_saatys_published_example():
    criteria = ["a", "b", "c"]
    judgements = {("b", "a"): 3, ("c", "a"): 5, ("c", "b"): 3}
    result = derive_weights(criteria, judgements)

    assert result.weights["a"] == pytest.approx(0.105, abs=0.002)
    assert result.weights["b"] == pytest.approx(0.258, abs=0.002)
    assert result.weights["c"] == pytest.approx(0.637, abs=0.002)
    assert result.lambda_max == pytest.approx(3.039, abs=0.002)
    assert result.consistency_ratio == pytest.approx(0.033, abs=0.002)
    assert result.is_consistent


def test_a_perfectly_consistent_matrix_has_zero_inconsistency():
    criteria = ["x", "y", "z"]
    # Weights 4:2:1 exactly.
    judgements = {("x", "y"): 2, ("y", "z"): 2, ("x", "z"): 4}
    result = derive_weights(criteria, judgements)

    assert result.lambda_max == pytest.approx(3.0, abs=1e-9)
    assert result.consistency_index == pytest.approx(0.0, abs=1e-9)
    assert result.consistency_ratio == pytest.approx(0.0, abs=1e-9)
    assert result.weights["x"] == pytest.approx(4 / 7)
    assert result.weights["y"] == pytest.approx(2 / 7)
    assert result.weights["z"] == pytest.approx(1 / 7)


def test_contradictory_judgements_are_flagged():
    criteria = ["a", "b", "c"]
    judgements = {("a", "b"): 9, ("b", "c"): 9, ("c", "a"): 9}
    result = derive_weights(criteria, judgements)

    assert result.consistency_ratio > CONSISTENCY_THRESHOLD
    assert not result.is_consistent
    assert "revisited" in result.verdict


def test_lambda_max_is_never_below_n():
    criteria = ["a", "b", "c", "d"]
    judgements = {
        ("a", "b"): 2,
        ("a", "c"): 5,
        ("a", "d"): 7,
        ("b", "c"): 2,
        ("b", "d"): 5,
        ("c", "d"): 3,
    }
    result = derive_weights(criteria, judgements)
    assert result.lambda_max >= len(criteria) - 1e-9


def test_weights_always_sum_to_one():
    criteria = ["a", "b", "c", "d", "e"]
    judgements = {("a", "b"): 3, ("b", "c"): 2, ("d", "e"): 4, ("a", "e"): 9}
    result = derive_weights(criteria, judgements)
    assert sum(result.weights.values()) == pytest.approx(1.0)


def test_eigenvector_and_geometric_mean_agree():
    """Two independent derivations of the same quantity."""
    matrix = build_matrix(RISK_CRITERIA, JUDGEMENTS)
    eigen = principal_eigenvector(matrix)
    geometric = geometric_mean_weights(matrix)
    for a, b in zip(eigen, geometric):
        assert a == pytest.approx(b, abs=0.01)


def test_reciprocals_are_filled_in_automatically():
    matrix = build_matrix(["a", "b"], {("a", "b"): 4})
    assert matrix[0][1] == 4.0
    assert matrix[1][0] == 0.25
    assert matrix[0][0] == matrix[1][1] == 1.0


def test_unknown_criterion_is_rejected():
    with pytest.raises(ValueError, match="unknown criterion"):
        build_matrix(["a", "b"], {("a", "zzz"): 3})


def test_non_positive_judgement_is_rejected():
    with pytest.raises(ValueError, match="must be positive"):
        build_matrix(["a", "b"], {("a", "b"): 0})


def test_duplicate_criteria_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        derive_weights(["a", "a"], {})


def test_two_criteria_cannot_be_inconsistent():
    result = derive_weights(["a", "b"], {("a", "b"): 7})
    assert result.consistency_ratio == 0.0
    assert result.is_consistent


def test_random_index_table_covers_our_size():
    assert len(RISK_CRITERIA) in RANDOM_CONSISTENCY_INDEX


def test_the_projects_own_judgements_are_consistent():
    """The weights the system actually runs on must pass Saaty's threshold."""
    assert RISK_WEIGHT_MODEL.is_consistent, RISK_WEIGHT_MODEL.verdict
    assert RISK_WEIGHT_MODEL.consistency_ratio < CONSISTENCY_THRESHOLD


def test_risk_weights_cover_every_criterion_and_sum_to_one():
    assert set(RISK_WEIGHTS) == set(RISK_CRITERIA)
    assert sum(RISK_WEIGHTS.values()) == pytest.approx(1.0)
    assert all(weight > 0 for weight in RISK_WEIGHTS.values())


def test_fall_risk_is_the_heaviest_criterion():
    heaviest = max(RISK_WEIGHTS, key=RISK_WEIGHTS.get)
    lightest = min(RISK_WEIGHTS, key=RISK_WEIGHTS.get)
    assert heaviest == "fall_risk"
    assert lightest == "recent_behaviour"
