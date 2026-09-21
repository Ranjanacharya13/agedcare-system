"""Print the AHP derivation of the resident risk weights."""

from backend.algorithms.ahp import (
    CONSISTENCY_THRESHOLD,
    RANDOM_CONSISTENCY_INDEX,
    build_matrix,
    geometric_mean_weights,
)
from backend.config.risk_weights import (
    JUDGEMENTS,
    RISK_CRITERIA,
    RISK_WEIGHT_MODEL,
)


def _format(value: float) -> str:
    """Reciprocals read better as 1/3 than as 0.3333."""
    if value >= 1:
        return f"{value:g}"
    return f"1/{round(1 / value):g}"


def main() -> int:
    model = RISK_WEIGHT_MODEL
    matrix = build_matrix(RISK_CRITERIA, JUDGEMENTS)
    width = max(len(name) for name in RISK_CRITERIA)

    print("\nPairwise comparison matrix (Saaty 1-9 scale)")
    print("  row i vs column j: how many times more important i is than j\n")
    header = " " * (width + 2) + "".join(f"{name[:10]:>12}" for name in RISK_CRITERIA)
    print(header)
    for i, name in enumerate(RISK_CRITERIA):
        row = "".join(f"{_format(value):>12}" for value in matrix[i])
        print(f"  {name:<{width}}{row}")

    print("\nDerived weights (principal eigenvector, power iteration)\n")
    geometric = dict(zip(RISK_CRITERIA, geometric_mean_weights(matrix)))
    for name in sorted(RISK_CRITERIA, key=lambda c: -model.weights[c]):
        weight = model.weights[name]
        bar = "#" * round(weight * 50)
        print(
            f"  {name:<{width}}  {weight * 100:5.1f}%  {bar}"
            f"   (geometric-mean cross-check {geometric[name] * 100:.1f}%)"
        )

    n = len(RISK_CRITERIA)
    print("\nConsistency\n")
    print(f"  lambda_max          {model.lambda_max:.6f}   (equals n = {n} when perfect)")
    print(f"  Consistency Index   {model.consistency_index:.6f}   CI = (lambda_max - n)/(n - 1)")
    print(
        f"  Random Index        {RANDOM_CONSISTENCY_INDEX[n]:.2f}"
        f"         RI for n = {n}, from Saaty's table"
    )
    print(f"  Consistency Ratio   {model.consistency_ratio:.6f}   CR = CI / RI")
    print(f"  Threshold           {CONSISTENCY_THRESHOLD}\n")
    print(f"  {model.verdict}\n")

    return 0 if model.is_consistent else 1


if __name__ == "__main__":
    raise SystemExit(main())
