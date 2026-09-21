# Decision algorithms

> SAW combines multiple weighted criteria into a score, while Lexicographic Ranking orders alternatives according to the priority of important criteria.

Flow: raw data → normalise criteria → SAW score → hard rules / priorities → lexicographic ranking → recommendation.

## 1. Algorithms used

1. **Simple Additive Weighting (SAW)** — `backend/algorithms/saw.py`
2. **Lexicographic Ranking** — `backend/algorithms/lexicographic.py`

Both are deterministic. There is no machine learning and no training data.

## 2. SAW

SAW combines several criteria into one score using weights.

```
S_i = Σ ( w_j × r_ij )
```

- `r_ij` = criterion *j* of alternative *i*, normalised to 0–1 (1 is always best)
- `w_j` = weight (importance) of criterion *j*; the weights sum to 1.0
- `S_i` = final score of alternative *i*, 0–1. **Higher score = better alternative**, everywhere in this project.

Worked example (from `demo_decision_algorithms.py`): weights care load 0.4, hours 0.2, skill 0.4.
Employee A has normalised values 0.50, 0.00, 0.67, so `S = 0.4×0.50 + 0.2×0.00 + 0.4×0.67 = 0.467`.

## 3. Why normalisation is needed

Care load might be 0–400, weekly hours 0–40 and skill 0–1. Added directly, care load would swamp everything else. Normalisation puts every criterion on the same 0–1 scale first.

We use min-max normalisation across the candidates being compared. If every candidate has the same value (max = min) they all get 1.0, so that criterion does not separate them.

## 4. Benefit vs cost criteria

- **Benefit** — higher is better (skill). `r = (value − min) / (max − min)`
- **Cost** — lower is better (care load, caseload, weekly hours). `r = (max − value) / (max − min)`

After normalisation both mean "higher r is better", so one SAW formula covers both.

## 5. Lexicographic ranking

Alternatives are compared on criteria in strict priority order, like words in a dictionary: the second criterion only matters if the first is equal. Shift example:

1. No conflict
2. Correct role
3. Higher SAW score
4. Lower care load, then lower weekly hours

In code, each candidate becomes a tuple such as `(conflict, -role_match, -saw_score, care_load)`. Python compares tuples left to right, which is exactly lexicographic order.

## 6. Why use both?

SAW suits criteria that can make up for each other (a bit more workload is fine if the skill fit is better). Lexicographic ranking suits criteria where strict priority matters. A low workload must not make up for a schedule conflict, so conflict is a priority rule and is **never** given a SAW weight.

## 7. Where each is used

| Feature | File | Method |
|---|---|---|
| Resident risk score | `services/risk_scoring.py` | SAW (weights from AHP) |
| Carer recommendation | `services/carer_matching.py` | SAW + lexicographic |
| Shift recommendation | `services/shift_matching.py` | SAW + lexicographic |
| Roster recommendation | `services/roster_optimisation.py` | SAW + lexicographic, one shift at a time |

### Weights and priorities

| Module | SAW criteria (weight) | Lexicographic priority |
|---|---|---|
| Risk score | fall risk, incidents, assistance, cognition, behaviour — AHP weights, see `config/risk_weights.py` | none (score only) |
| Carer matching | risk load 0.33, caseload 0.17, acuity fit 0.50 | role suitable → SAW score → smaller caseload |
| Shift / roster | care load 0.625, weekly hours 0.375 | no conflict → role match → SAW score → care load → weekly hours |

Hard rules applied before ranking: inactive employees are rejected; for carers, anyone already on the resident's care team is rejected. The weights keep the balance the old cost model used (carer 1.0 : 0.5 : 1.5, shift 1.0 : 0.6), scaled to sum to 1.

`acuity fit = 1 − resident acuity × (1 − role skill)` is already 0–1, so it needs no min-max step. It is what makes the ranking depend on the *pair*: a sicker resident penalises a low-skill role more.

Roster: shifts are handled earliest first. Each recommendation is remembered, so the same employee is never recommended for two overlapping shifts, and their planned hours count towards later shifts. This is a greedy, explainable recommendation, **not** a mathematically optimal roster.

## 8. Why not machine learning?

No training data is needed, decisions are deterministic, every score can be explained criterion by criterion, and that suits a university aged-care system.

## 9. Why not the Hungarian algorithm?

The Hungarian algorithm solves a different problem: a globally optimal one-to-one assignment. Here the main requirement is transparent multi-criteria recommendation and ranking. SAW lets every important criterion contribute to suitability, and lexicographic ranking lets hard priorities such as conflicts and roles come first. The same two ideas apply consistently across all recommendation modules and are easy to explain.

## 10. Complexity

- SAW: *n* alternatives × *m* criteria → **O(n × m)**
- Lexicographic sort: about **O(n log n × k)** for *k* priority criteria

## 11. Advantages

- **SAW:** simple, transparent, fast, weighted, explainable, no training data.
- **Lexicographic:** easy to understand, supports strict priorities, deterministic, good for hard business rules.

## 12. Limitations

- SAW results depend on the chosen weights.
- Lexicographic results depend strongly on the priority order.
- These provide decision support and recommendations, not clinical judgment. A person always confirms.

## Try it

```bash
uv run python -m backend.scripts.demo_decision_algorithms
uv run pytest backend/tests/test_saw.py backend/tests/test_lexicographic.py
```
