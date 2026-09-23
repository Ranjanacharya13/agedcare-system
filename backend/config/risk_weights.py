"""Resident risk weights for Simple Additive Weighting (SAW).

Weights are established via Direct Point Allocation (SMART methodology) aligned with
Australian Aged Care Quality and Safety Commission (ACQSC) standards and SIRS (Serious
Incident Response Scheme) data:
  - fall_risk (0.34): Primary cause of preventable physical injury and hospital transfers
  - recent_incidents (0.26): Track record of acute clinical incidents under SIRS
  - assistance_level (0.18): Physical transfer and ADL mobility dependency (AN-ACC aligned)
  - cognitive_status (0.14): Dementia and cognitive impairment classification
  - recent_behaviour (0.08): Behavioural and psychological symptoms of dementia (BPSD)
"""

from backend.algorithms.saw import check_weights

RISK_CRITERIA: list[str] = [
    "fall_risk",
    "recent_incidents",
    "assistance_level",
    "cognitive_status",
    "recent_behaviour",
]

#: Direct domain weights for Simple Additive Weighting (SAW).
#: The weights reflect clinical priority in aged care and sum to 1.0.
RISK_WEIGHTS: dict[str, float] = {
    "fall_risk": 0.34,
    "recent_incidents": 0.26,
    "assistance_level": 0.18,
    "cognitive_status": 0.14,
    "recent_behaviour": 0.08,
}

check_weights(RISK_WEIGHTS)

INCIDENT_SATURATION = 6.0

#: Behaviour events in the lookback window at which that signal saturates.
BEHAVIOUR_SATURATION = 4.0

INCIDENT_LOOKBACK_DAYS = 90
BEHAVIOUR_LOOKBACK_DAYS = 30
