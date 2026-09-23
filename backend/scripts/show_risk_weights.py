"""Print the Simple Additive Weighting (SAW) resident risk weights."""

from backend.algorithms.saw import check_weights
from backend.config.risk_weights import RISK_CRITERIA, RISK_WEIGHTS

CLINICAL_RATIONALE = {
    "fall_risk": "Primary cause of preventable physical injury and hospital transfers in RACFs",
    "recent_incidents": "Track record of acute adverse clinical events under the SIRS framework",
    "assistance_level": "Physical mobility and transfer dependency (AN-ACC assessment category)",
    "cognitive_status": "Dementia classification and cognitive impairment level",
    "recent_behaviour": "Behavioural episodes and BPSD (Behavioural and Psychological Symptoms of Dementia)",
}


def main() -> int:
    check_weights(RISK_WEIGHTS)
    width = max(len(name) for name in RISK_CRITERIA)

    print("\nResident Risk Scoring Model: Simple Additive Weighting (SAW)")
    print("Clinical Policy: Direct Point Allocation (SMART method, Australian ACQSC & SIRS aligned)\n")
    print(f"  {'Criterion':<{width}}  {'Weight':>8}  {'Percent':>8}  {'Max Pts':>8}  {'Clinical Rationale'}")
    print("  " + "-" * (width + 75))

    for name in sorted(RISK_CRITERIA, key=lambda c: -RISK_WEIGHTS[c]):
        weight = RISK_WEIGHTS[name]
        percentage = weight * 100
        max_pts = round(100 * weight)
        rationale = CLINICAL_RATIONALE.get(name, "")
        bar = "#" * round(weight * 30)
        print(f"  {name:<{width}}  {weight:8.4f}  {percentage:7.1f}%  {max_pts:6d} pts  {rationale}")

    total_weight = sum(RISK_WEIGHTS.values())
    print("  " + "-" * (width + 75))
    print(f"  {'TOTAL':<{width}}  {total_weight:8.4f}  {total_weight * 100:7.1f}%  {round(100 * total_weight):6d} pts\n")

    print("Formula: Resident Risk Score = 100 x sum( weight_j x normalised_signal_j )")
    print("Range:   0 to 100 (Bands: Low < 25, Medium 25-49, High 50-74, Critical 75-100)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
