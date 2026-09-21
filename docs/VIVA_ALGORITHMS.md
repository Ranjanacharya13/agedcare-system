# Viva answers: SAW + Lexicographic Ranking

**30 seconds.** First, the system collects the relevant criteria. SAW normalises and weights them to produce an overall suitability score from 0 to 1. Then lexicographic ranking applies strict priorities, such as no shift conflict and a compatible role, before the score is even looked at. The system finally ranks the alternatives from most to least suitable, and every score can be explained criterion by criterion.

**60 seconds.** For carers and shifts, each candidate has raw data such as care load, weekly hours and role. Cost criteria (lower is better) and benefit criteria (higher is better) are min-max normalised to 0–1 so different units are comparable. SAW multiplies each by its weight and adds them: S = Σ(w × r). Higher is better everywhere. Hard rules like schedule conflict and role compatibility are not weights, because a low workload must never compensate for a conflict. They are the first priorities in a lexicographic ranking, implemented as tuple sorting. The SAW score decides only when those are equal, then smaller workload breaks ties. For the roster, shifts are processed in time order and each recommendation is remembered so nobody is double-booked. Resident risk uses SAW with AHP-derived weights. It is all deterministic, with no machine learning.

**Q: Which algorithms did you use?**
Simple Additive Weighting and Lexicographic Ranking.

**Q: What does SAW do?**
It normalises different criteria, multiplies each by its importance weight, and adds them to give an overall score.

**Q: What is the formula?**
S_i = Σ(w_j × r_ij)

**Q: Why normalise?**
Criteria such as hours, workload and skill use different scales, so they cannot be added directly.

**Q: Why use weights?**
Some criteria are more important than others.

**Q: What does a higher SAW score mean?**
A more suitable alternative. This holds in every module.

**Q: What is the difference between benefit and cost criteria?**
Benefit: higher is better, `(v − min)/(max − min)`. Cost: lower is better, `(max − v)/(max − min)`. After normalising, higher is better for both.

**Q: What if all candidates have the same value?**
Max equals min, so normalisation would divide by zero. That criterion scores 1.0 for everyone and does not separate them.

**Q: What is Lexicographic Ranking?**
It compares alternatives on criteria in strict priority order, like a dictionary.

**Q: Why use Lexicographic Ranking with SAW?**
Some criteria must not be compensated for by others. An employee with a scheduling conflict should not rank first just because their workload is low.

**Q: How is it implemented?**
Each candidate becomes a tuple, and Python compares tuples left to right, which is lexicographic order.

**Q: Where does the resident risk score fit?**
It is SAW: a weighted sum of five normalised signals, scaled to 0–100, with AHP-derived weights.

**Q: Are they machine learning? Do they need training data?**
No to both. They are deterministic multi-criteria decision methods.

**Q: Why are they appropriate for aged care?**
Several factors matter (workload, risk, role, hours, availability) and recommendations must stay transparent.

**Q: Is the roster optimal?**
No. Shifts are handled earliest first, each with the best-ranked free employee. It is an explainable recommendation, not a global optimum.

**Q: What is the complexity of SAW?**
O(n × m) for n alternatives and m criteria. Sorting adds about O(n log n × k).

**Q: Main weakness of SAW?**
The result depends on choosing appropriate criteria and weights.

**Q: Main weakness of Lexicographic Ranking?**
The priority order has a strong influence on the result.

**Q: Why didn't you use Hungarian?**
Hungarian finds a globally optimal one-to-one assignment. Our system mainly needs explainable multi-criteria scoring and ranking, so SAW and lexicographic ranking fit our decision-support design better.
