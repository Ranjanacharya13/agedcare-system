"""Where the resident risk weights come from."""

from backend.algorithms.ahp import derive_weights

RISK_CRITERIA = [
    "fall_risk",
    "recent_incidents",
    "assistance_level",
    "cognitive_status",
    "recent_behaviour",
]

JUDGEMENTS: dict[tuple[str, str], float] = {
    ("fall_risk", "recent_incidents"): 1,
    ("fall_risk", "assistance_level"): 2,
    ("fall_risk", "cognitive_status"): 3,
    ("fall_risk", "recent_behaviour"): 4,
    ("recent_incidents", "assistance_level"): 1,
    ("recent_incidents", "cognitive_status"): 2,
    ("recent_incidents", "recent_behaviour"): 3,
    ("assistance_level", "cognitive_status"): 1,
    ("assistance_level", "recent_behaviour"): 2,
    ("cognitive_status", "recent_behaviour"): 2,
}

RISK_WEIGHT_MODEL = derive_weights(RISK_CRITERIA, JUDGEMENTS)

#: criterion -> weight in [0, 1]; the five sum to 1.
RISK_WEIGHTS = RISK_WEIGHT_MODEL.weights


INCIDENT_SATURATION = 6.0

#: Behaviour events in the lookback window at which that signal saturates.
BEHAVIOUR_SATURATION = 4.0

INCIDENT_LOOKBACK_DAYS = 90
BEHAVIOUR_LOOKBACK_DAYS = 30
