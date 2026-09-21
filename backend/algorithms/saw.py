"""Simple Additive Weighting (SAW).

    S_i = sum over criteria j of ( w_j * r_ij )

r_ij = criterion j of alternative i, normalised to 0..1 (1 is always best)
w_j  = importance weight of criterion j (all weights sum to 1)
S_i  = overall score of alternative i, 0..1. Higher score = better alternative.
"""

TOLERANCE = 1e-9


def normalize_benefit(value: float, minimum: float, maximum: float) -> float:
    """Benefit criterion: higher is better (e.g. skill)."""
    if maximum == minimum:
        return 1.0  # everyone is equal, so nobody is penalised
    return (value - minimum) / (maximum - minimum)


def normalize_cost(value: float, minimum: float, maximum: float) -> float:
    """Cost criterion: lower is better (e.g. workload)."""
    if maximum == minimum:
        return 1.0
    return (maximum - value) / (maximum - minimum)


def normalize_all(values: list[float], benefit: bool = False) -> list[float]:
    """Min-max normalise one criterion across all alternatives."""
    if not values:
        return []
    normalize = normalize_benefit if benefit else normalize_cost
    low, high = min(values), max(values)
    return [normalize(v, low, high) for v in values]


def check_weights(weights: dict[str, float]) -> None:
    if abs(sum(weights.values()) - 1.0) > TOLERANCE:
        raise ValueError(f"weights must sum to 1.0, got {sum(weights.values())}")


def calculate_saw_score(normalised: dict[str, float], weights: dict[str, float]) -> float:
    """Multiply each normalised criterion by its weight and add them up."""
    check_weights(weights)
    return sum(weights[name] * normalised[name] for name in weights)


def saw_breakdown(
    normalised: dict[str, float], weights: dict[str, float], raw: dict | None = None
) -> list[dict]:
    """One line per criterion, so a score can be explained. Contributions sum to the score."""
    raw = raw or {}
    return [
        {
            "criterion": name,
            "value": raw.get(name),
            "normalised": round(normalised[name], 4),
            "weight": weight,
            "contribution": round(weight * normalised[name], 4),
        }
        for name, weight in weights.items()
    ]
