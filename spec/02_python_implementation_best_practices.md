# Python Implementation Best Practices
## Dynamic ASP Allocation Optimizer Demo

> Purpose: this file provides implementation guidance for building the demo in Python. It is intended for Kiro-cli or another coding agent.

---

## 1. Recommended Technology Stack

Prefer a simple Python-based demo stack.

Recommended default:

```text
Python 3.11+
Streamlit for interactive UI
Pandas and NumPy for data processing
Plotly for interactive charts
SciPy optimize or PuLP for allocation optimization
Pydantic or dataclasses for typed configuration
Pytest for tests
```

Alternative UI options:

```text
Dash
Panel
FastAPI backend + React frontend
Jupyter notebook only for prototyping, not for final demo
```

For the initial demo, use **Streamlit** because it is fast to build, easy to present, and stakeholder-friendly.

---

## 2. Suggested Project Structure

```text
asp_allocation_demo/
│
├── app.py
├── README.md
├── requirements.txt
│
├── config/
│   ├── default_settings.yaml
│   └── scenario_templates.yaml
│
├── src/
│   ├── __init__.py
│   ├── data_generator.py
│   ├── data_quality.py
│   ├── scoring.py
│   ├── causal_layer.py
│   ├── sme_layer.py
│   ├── constraints.py
│   ├── optimizer.py
│   ├── scenarios.py
│   ├── rebalancing.py
│   ├── explanations.py
│   └── visualization.py
│
├── tests/
│   ├── test_data_generator.py
│   ├── test_data_quality.py
│   ├── test_scoring.py
│   ├── test_constraints.py
│   ├── test_optimizer.py
│   └── test_scenarios.py
│
└── assets/
    └── optional_static_images_or_icons/
```

---

## 3. Key Design Principles

### 3.1 Keep business logic separate from UI

Do not put all logic inside `app.py`.

`app.py` should only:

- Handle user inputs
- Call engine functions
- Display outputs
- Manage session state

Core logic should live in `src/` modules.

---

### 3.2 Make the demo deterministic when needed

Use a random seed.

The UI should allow:

```text
Random seed: 42
[Generate Synthetic Data]
```

This lets the presenter reproduce the same flow during a live presentation.

---

### 3.3 Use business labels by default

Default UI must not expose technical jargon.

Use:

```text
Data Confidence Layer
Causal Intelligence Layer
Allocation Engine
Management Simulator
```

Only show technical names inside collapsed expanders.

---

### 3.4 Maintain explainability

Every recommendation must have reason codes.

Good reason code example:

```text
Climb ASP 3 receives 60% because:
+ Best safety score
+ Strongest certified workforce
+ Lowest repeat visit rate
- Capacity close to limit
```

Avoid black-box recommendations.

---

## 4. Data Generation Best Practices

### 4.1 Generate task-level data

Generate one row per task. Aggregate later.

Minimum required columns:

```text
task_id
week
profile
region
asp
task_type
task_complexity_score
estimated_job_duration
distance_to_site_km
travel_time_minutes
weather_risk
site_access_difficulty
security_restriction
required_certification
asp_certified_staff_available
technician_fatigue_risk
manual_escalation_flag
emergency_task_flag
customer_segment
sla_class
cost_per_task
completed_within_sla
repeat_visit_required
nps_score
safety_incident_flag
data_confidence_score
```

Important: `actual_delivery_time` and `time_of_delivery` should not be included as KPIs. Travel time may exist as a causal/context variable, but it should not be shown as one of the main business KPIs.

---

### 4.2 Create controlled patterns

Synthetic data should be realistic and explainable.

Examples:

```text
Urban ASP 1: cheap and stable, average NPS
Urban ASP 2: best SLA and NPS, higher cost
Urban ASP 3: good on simple jobs, weaker on complex installations

Mountain ASP 1: receives hardest emergency jobs, raw SLA looks weak
Mountain ASP 2: best standard-task performance
Mountain ASP 3: backup capacity, moderate performance

Climb ASP 1: low cost but safety caution
Climb ASP 2: certified and balanced
Climb ASP 3: strongest safety, limited capacity
```

---

### 4.3 Intentionally inject data quality issues

The synthetic generator must create:

```text
Missing NPS values
Small sample sizes
Outliers
Noise
Sparse safety events
Assignment bias
Weather/security effects
Certification gaps
```

This supports the Data Confidence Layer.

---

## 5. Data Confidence Layer Best Practices

### 5.1 Use simple Bayesian smoothing

Use smoothing for KPIs with sparse samples, especially NPS and safety-related indicators.

Business explanation:

```text
If an ASP has only a few observations, do not trust the raw number too much.
Pull it toward a reasonable profile-level baseline and show confidence.
```

Suggested formula:

```text
smoothed_value = (observed_value * n + baseline_value * smoothing_strength) / (n + smoothing_strength)
```

Where:

```text
n = number of observations
baseline_value = profile-level or global average
smoothing_strength = how strongly to trust the baseline
```

### 5.2 Track confidence

Use simple confidence labels:

```text
High: enough data and low missingness
Medium: moderate sample or some missingness
Low: small sample, sparse data or high missingness
```

---

## 6. Scoring Best Practices

### 6.1 Normalize metrics

Convert all KPI metrics to a 0–100 score.

Positive direction metrics:

```text
Safety score
SLA compliance
NPS
Certified capacity coverage
```

Negative direction metrics:

```text
Cost per task
Repeat visit rate
Budget usage
```

### 6.2 Use weighted scoring

Recommended default weights:

```text
Cost: 20%
Safety/Security: 30%
SLA: 25%
NPS: 15%
Repeat Visits: 10%
```

Weights should be adjustable in the UI.

### 6.3 Treat safety differently for Climb

Safety for Climb must be both:

1. A scoring factor
2. A hard eligibility gate

Example:

```text
If Climb safety score < 90, ASP is not eligible for Climb tasks.
If required certification is missing, ASP receives 0 Climb tasks.
```

---

## 7. Causal Intelligence Best Practices

### 7.1 Show naive vs adjusted view

The demo must show:

```text
Raw KPI ranking
Then task context
Then SME observation
Then adjusted recommendation
```

### 7.2 Capture causal variables

Generate variables such as:

```text
task_complexity_score
site_access_difficulty
weather_risk
emergency_task_flag
manual_escalation_flag
reassigned_task_flag
customer_access_issue_flag
customer_segment
sla_class
region
week
```

### 7.3 Simulate assignment bias

Example:

```text
Mountain ASP 1 receives more emergency and high-complexity tasks.
Therefore raw SLA is lower.
The causal layer prevents unfair penalty.
```

### 7.4 Apply causal adjustments simply

For demo purposes, avoid complex causal libraries unless necessary.

Use transparent rules such as:

```text
If ASP receives significantly harder tasks than profile average,
show adjusted interpretation and protect against excessive volume reduction.
```

The goal is to demonstrate cause-and-effect thinking, not to prove a full academic causal model.

---

## 8. SME Layer Best Practices

### 8.1 Represent SME observations as structured data

Each SME note should have:

```text
note_id
source_role
profile
asp
business_observation
confidence_level
valid_from
valid_until
engine_effect
```

### 8.2 SME notes must affect the engine

Examples:

```text
Observation: ASP 1 quality drops above 45% share.
Effect: max share for ASP 1 = 45%.

Observation: Climb ASP 1 changed supervisors.
Effect: temporary safety caution factor or lower max Climb share.

Observation: ASP 3 completed new training.
Effect: allow gradual controlled increase in allocation.
```

### 8.3 Show SME notes visually

Use sticky-note cards in the UI.

---

## 9. Constraints Best Practices

### 9.1 Separate hard constraints from preferences

Hard constraints:

```text
Capacity
Budget
Climb certification
Safety threshold
Security eligibility
```

Soft preferences:

```text
Cost minimization
NPS improvement
Repeat visit reduction
Balanced ASP allocation
```

### 9.2 Required constraints

The optimizer must handle:

```text
Demand fulfillment
ASP capacity
Budget limit
Safety threshold for Climb
Certification eligibility for Climb
Weather/security capacity reduction
Maximum share per ASP
Minimum share for eligible ASPs if feasible
SME-driven caps
```

### 9.3 Explain infeasibility

If no feasible allocation exists, show:

```text
No feasible allocation found.
Main blockers:
- Certified Climb capacity is insufficient.
- Budget is too low.
- Weather restrictions reduce Mountain capacity below demand.
Suggested actions:
- Increase budget.
- Add certified capacity.
- Relax max share cap.
```

---

## 10. Optimization Best Practices

### 10.1 Use continuous allocation for first version

The first demo can allocate percentages or task counts continuously.

This is sufficient for a business demo.

Use integer allocation only if required.

### 10.2 Objective

Maximize total business value:

```text
maximize sum(score[profile, asp] * allocation[profile, asp])
```

Subject to constraints.

### 10.3 Fallback if optimization package is unavailable

If PuLP or another solver is unavailable, implement a greedy constrained allocator:

```text
1. Remove ineligible ASPs.
2. Apply minimum shares where feasible.
3. Sort ASPs by score.
4. Allocate remaining demand to highest-score ASPs until capacity, max share or budget is reached.
5. If demand remains unmet, mark infeasible.
```

This is acceptable for a demo if reason codes are clear.

---

## 11. Scenario Best Practices

Each scenario should modify a small number of inputs and rerun the engine.

Required scenarios:

```text
Balanced Mode
Cost Pressure
SLA Recovery
Bad Mountain Weather
Climb Certification Issue
Next Month Rebalance
```

### Cost Pressure

```text
Budget reduced by 15%.
Cost weight increases.
```

### SLA Recovery

```text
SLA weight increases.
SLA underperformers receive lower allocation.
```

### Bad Mountain Weather

```text
Mountain weather risk becomes High.
Mountain capacity reduced.
```

### Climb Certification Issue

```text
One Climb ASP loses certification.
That ASP receives zero Climb allocation.
```

### Next Month Rebalance

```text
Performance metrics are updated.
Improving ASPs receive gradual increase.
Deteriorating ASPs receive reduction.
```

---

## 12. Dynamic Rebalancing Best Practices

Use a simple update formula:

```text
updated_score = recent_weight * recent_score + historical_weight * historical_score
```

Default:

```text
recent_weight = 0.70
historical_weight = 0.30
```

Add caution:

```text
Do not overreact to one bad week.
Use caps on how much allocation can change between periods.
```

Suggested allocation movement cap:

```text
Maximum change per planning cycle: 15 percentage points
```

---

## 13. Visualization Best Practices

Use visuals that work for business stakeholders.

Recommended charts:

```text
KPI cards
Stacked horizontal allocation bars
Before/after KPI cards
Traffic-light confidence indicators
Radar chart or grouped bar chart for ASP scorecard
Sticky-note cards for SME observations
Scenario comparison cards
Timeline for dynamic rebalancing
```

Avoid:

```text
Large raw-data tables as the default view
Complex formulas on the main page
Dense statistical charts without explanation
```

---

## 14. Streamlit UI Best Practices

Recommended layout:

```text
st.tabs([
  "Setup",
  "Data Confidence",
  "Business Priorities",
  "Causal Intelligence",
  "Constraints",
  "Recommendation",
  "Scenarios"
])
```

Use:

```text
st.metric for KPI cards
st.expander for hidden technical details
st.slider for priorities and constraints
st.toggle or st.checkbox for constraint activation
st.plotly_chart for visualizations
st.dataframe only inside expanders or engine view
```

Use Streamlit session state for:

```text
generated_data
settings
constraints
scenario
recommendations
engine_log
```

---

## 15. Testing Best Practices

At minimum, implement tests for:

```text
Data generator creates required columns
Missing values are generated intentionally
Bayesian smoothing behaves correctly
Scores are between 0 and 100
Climb ineligible ASP receives zero tasks
Budget constraint is respected
Capacity constraint is respected
SME caps are respected
Infeasibility is detected
Scenario changes recommendation
Time of delivery is not included as a KPI
```

---

## 16. Performance Best Practices

The app should be responsive during a live demo.

Guidelines:

```text
Generate 1,000 to 5,000 task records by default.
Avoid heavy computations on every UI interaction.
Cache generated synthetic data when possible.
Rerun optimization only when inputs change.
Keep solver model small: 3 profiles x 3 ASPs.
```

---

## 17. Governance and Production Notes

The demo should include hidden production guidance:

```text
Keep audit trail of recommendations.
Store input data, constraints, weights and SME assumptions.
Track model drift and data quality over time.
Require human approval for high-impact allocation changes.
Never automate safety overrides without governance.
Use role-based permissions for changing constraints and business weights.
```

---

## 18. Implementation Acceptance Criteria

A generated implementation is acceptable if:

1. It runs locally using Python.
2. It generates synthetic task-level data dynamically.
3. It shows medium data quality by design.
4. It processes incomplete data with smoothing or confidence adjustment.
5. It shows business priorities and adjustable weights.
6. It includes causal context and SME observations.
7. It applies operational constraints.
8. It recommends allocation by profile and ASP.
9. It explains recommendations with reason codes.
10. It includes what-if scenarios.
11. It supports dynamic rebalancing.
12. It hides technical information by default.
13. It excludes time of delivery from the business KPI list.
14. It is understandable for non-technical stakeholders.
