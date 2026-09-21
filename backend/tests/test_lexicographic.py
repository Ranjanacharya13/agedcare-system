"""Lexicographic ranking: earlier criteria always beat later ones."""

from backend.algorithms.lexicographic import rank

PRIORITY = (("conflict", False), ("role_match", True), ("saw_score", True), ("hours", False))


def item(name, conflict=False, role_match=True, saw_score=0.5, hours=10):
    return dict(name=name, conflict=conflict, role_match=role_match, saw_score=saw_score, hours=hours)


def names(items):
    return [i["name"] for i in rank(items, PRIORITY)]


def test_no_conflict_beats_conflict_even_with_a_much_better_saw_score():
    assert names([item("B", conflict=True, saw_score=0.95), item("A", saw_score=0.72)]) == ["A", "B"]


def test_matching_role_beats_wrong_role():
    wrong = item("wrong", role_match=False, saw_score=0.9)
    assert names([wrong, item("right", saw_score=0.1)]) == ["right", "wrong"]


def test_saw_score_decides_when_priority_criteria_are_equal():
    assert names([item("low", saw_score=0.3), item("high", saw_score=0.8)]) == ["high", "low"]


def test_tie_breaker_is_used_when_saw_scores_are_equal():
    assert names([item("busy", hours=30), item("free", hours=5)]) == ["free", "busy"]


def test_ranking_is_deterministic():
    items = [item("A"), item("B"), item("C", saw_score=0.9)]
    assert names(items) == names(items) == ["C", "A", "B"]
