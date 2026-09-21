"""Lexicographic ranking: compare alternatives criterion by criterion, in priority order.

Like a dictionary: the second letter only matters if the first letters are equal.
A later criterion (e.g. the SAW score) can never beat an earlier one (e.g. a conflict).
"""


def rank(items: list[dict], priority: tuple[tuple[str, bool], ...]) -> list[dict]:
    """Best first. priority = ((field, higher_is_better), ...), most important first."""

    def key(item: dict) -> tuple:
        # Python compares tuples left to right, which is exactly lexicographic order.
        # Sorting ascending puts the smallest first, so higher-is-better fields are negated.
        # False < True, so a bool field "conflict" with higher_is_better=False puts False first.
        return tuple(-float(item[f]) if higher else float(item[f]) for f, higher in priority)

    return sorted(items, key=key)  # sorted() is stable, so equal items keep their input order
