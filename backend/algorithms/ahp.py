"""Analytic Hierarchy Process: pairwise judgements to weights, plus a consistency check."""

from __future__ import annotations

from dataclasses import dataclass

RANDOM_CONSISTENCY_INDEX = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
}

#: Saaty's rule of thumb for acceptable inconsistency.
CONSISTENCY_THRESHOLD = 0.10

#: The 1-9 scale, for anyone reading the judgement table.
SAATY_SCALE = {
    1: "equally important",
    2: "slightly toward moderate",
    3: "moderately more important",
    4: "moderate toward strong",
    5: "strongly more important",
    6: "strong toward very strong",
    7: "very strongly more important",
    8: "very strong toward extreme",
    9: "extremely more important",
}


@dataclass(frozen=True)
class AHPResult:
    criteria: list[str]
    weights: dict[str, float]
    lambda_max: float
    consistency_index: float
    consistency_ratio: float

    @property
    def is_consistent(self) -> bool:
        return self.consistency_ratio < CONSISTENCY_THRESHOLD

    @property
    def verdict(self) -> str:
        if self.is_consistent:
            return (
                f"Consistent (CR = {self.consistency_ratio:.3f} < {CONSISTENCY_THRESHOLD}); "
                "the pairwise judgements support these weights."
            )
        return (
            f"Inconsistent (CR = {self.consistency_ratio:.3f} >= {CONSISTENCY_THRESHOLD}); "
            "the pairwise judgements contradict each other and should be revisited."
        )


def build_matrix(criteria: list[str], judgements: dict[tuple[str, str], float]) -> list[list[float]]:
    """Expand a sparse set of judgements into the full reciprocal matrix."""
    index = {name: i for i, name in enumerate(criteria)}
    n = len(criteria)
    matrix = [[1.0] * n for _ in range(n)]

    for (left, right), value in judgements.items():
        if left not in index or right not in index:
            raise ValueError(f"Judgement references unknown criterion: {left!r} vs {right!r}")
        if value <= 0:
            raise ValueError(f"Judgement for {left} vs {right} must be positive, got {value}")
        i, j = index[left], index[right]
        matrix[i][j] = float(value)
        matrix[j][i] = 1.0 / float(value)

    return matrix


def _normalise(vector: list[float]) -> list[float]:
    total = sum(vector)
    if total == 0:
        raise ValueError("Cannot normalise a zero vector")
    return [value / total for value in vector]


def principal_eigenvector(
    matrix: list[list[float]], *, max_iterations: int = 1000, tolerance: float = 1e-12
) -> list[float]:
    """Power iteration."""
    n = len(matrix)
    vector = [1.0 / n] * n

    for _ in range(max_iterations):
        product = [sum(matrix[i][j] * vector[j] for j in range(n)) for i in range(n)]
        nxt = _normalise(product)
        if max(abs(a - b) for a, b in zip(nxt, vector)) < tolerance:
            return nxt
        vector = nxt

    return vector


def geometric_mean_weights(matrix: list[list[float]]) -> list[float]:
    """Saaty's row-geometric-mean approximation."""
    n = len(matrix)
    means = []
    for row in matrix:
        product = 1.0
        for value in row:
            product *= value
        means.append(product ** (1.0 / n))
    return _normalise(means)


def derive_weights(
    criteria: list[str], judgements: dict[tuple[str, str], float]
) -> AHPResult:
    """Full AHP pass: judgements in, weights plus a consistency verdict out."""
    if len(criteria) < 2:
        raise ValueError("AHP needs at least two criteria to compare")
    if len(set(criteria)) != len(criteria):
        raise ValueError("Criteria must be unique")

    matrix = build_matrix(criteria, judgements)
    n = len(criteria)
    weights = principal_eigenvector(matrix)

    weighted_sums = [sum(matrix[i][j] * weights[j] for j in range(n)) for i in range(n)]
    lambda_max = sum(ws / w for ws, w in zip(weighted_sums, weights)) / n

    consistency_index = (lambda_max - n) / (n - 1)
    random_index = RANDOM_CONSISTENCY_INDEX.get(n, 1.49)
    # n <= 2 cannot be inconsistent: there is only one judgement to make.
    consistency_ratio = 0.0 if random_index == 0 else consistency_index / random_index

    return AHPResult(
        criteria=list(criteria),
        weights={name: weight for name, weight in zip(criteria, weights)},
        lambda_max=lambda_max,
        consistency_index=consistency_index,
        consistency_ratio=consistency_ratio,
    )
