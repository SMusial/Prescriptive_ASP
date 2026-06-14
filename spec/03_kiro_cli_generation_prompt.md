# Kiro-cli Generation Prompt
## Build the Dynamic ASP Allocation Optimizer Demo

Use this file as the main generation prompt for Kiro-cli.

---

## Goal

Create a Python Streamlit demo named **Dynamic ASP Allocation Optimizer**.

The app demonstrates prescriptive analytics for telco field services. It recommends how to split field-service task volumes across ASPs for three profiles:

```text
Urban
Mountain
Climb
```

Each profile has three ASPs.

The app must be business-focused, visual, simple for stakeholders, and hide technical details by default.

---

## Key Business Question

```text
How should we split field-service task volume across ASPs, considering cost, safety/security, SLA, NPS, repeat visits, capacity, weather/security risk, certifications, budget, data quality, causal context, and SME knowledge?
```

Do not use **time of delivery** as a KPI.

---

## Required App Sections

Create a Streamlit app with these tabs:

```text
1. Setup
2. Data Confidence
3. Business Priorities
4. Causal Intelligence
5. Constraints
6. Recommendation
7. Scenarios
8. Engine View
```

`Engine View` must be collapsed or clearly technical by default.

---

## Required Capabilities

The app must demonstrate five prescriptive analytics capabilities using business-friendly names:

```text
Business Scorecard
Data Confidence Layer
Causal Intelligence Layer
Allocation Engine
Management Simulator
```

Technical method names should appear only inside expanders.

---

## Synthetic Data Generation

Implement a dynamic data generator with a random seed.

Generate task-level data with columns:

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

Important:

- `travel_time_minutes` may be used as a context/causal variable.
- Do not show time of delivery as a KPI.
- Do not optimize on time of delivery as a KPI.

Generate realistic patterns:

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

Inject data quality issues:

```text
Missing NPS values
Small samples
Outliers
Noise
Sparse safety events
Assignment bias
Weather/security effects
Certification gaps
```

---

## Data Confidence Layer

Implement Bayesian-style smoothing for sparse metrics, especially NPS and safety-related metrics.

Use a simple formula:

```text
smoothed_value = (observed_value * n + baseline_value * smoothing_strength) / (n + smoothing_strength)
```

Show:

```text
Missing NPS percentage
Low sample metric percentage
Outlier count
Safety data sparsity
Overall data confidence
Before/after smoothed metrics
```

Use simple labels:

```text
High confidence
Medium confidence
Low confidence
```

---

## Business Priorities

Create sliders for:

```text
Cost
Safety/Security
SLA
NPS
Repeat Visits
```

Default weights:

```text
Cost: 20
Safety/Security: 30
SLA: 25
NPS: 15
Repeat Visits: 10
```

Normalize weights internally.

Use these to compute ASP business scores.

---

## Scoring

Aggregate task-level data to ASP/profile level.

Compute normalized 0–100 scores for:

```text
Cost score: lower cost is better
Safety score: higher is better
SLA score: higher is better
NPS score: higher is better
Repeat visit score: lower repeat visit rate is better
Certified capacity coverage score: higher is better
```

Compute total business score using the priority weights.

For Climb, safety and certification must be hard gates.

---

## Causal Intelligence Layer

Show a dedicated tab explaining why raw KPIs can be misleading.

Required demo example:

```text
Raw Mountain SLA ranking shows Mountain ASP 2 as best and Mountain ASP 1 as weak.
Then reveal that Mountain ASP 1 receives harder emergency tasks with higher complexity and travel difficulty.
Then show that the recommendation changes after causal context and SME knowledge are applied.
```

Show:

```text
Raw Mountain SLA ranking bar chart
Task difficulty comparison
Emergency share comparison
SME sticky notes
Naive decision vs causal decision
```

Simulate causal adjustment with transparent logic.

Example:

```text
If ASP has much higher task complexity and emergency share than profile average,
avoid excessive penalty from raw SLA.
```

---

## SME Observation Layer

Create structured SME observations.

Each note must include:

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

Include at least these SME observations:

```text
Safety Manager: Climb ASP 1 recently changed two senior supervisors. Formal audit is still valid, but operational confidence is lower for high-risk sites.

Dispatcher: Mountain ASP 1 is often used for difficult emergency jobs because they know the region best.

Operations Manager: ASP 1 quality drops when share exceeds 45% because they rely more on subcontractors.

Contract Manager: Repeat visits for Climb tasks have greater reputational impact than Urban repeat visits.

Regional Expert: Two Mountain zones become risky after heavy rain.
```

SME observations must affect the recommendation.

Examples:

```text
Max share cap 45% for ASP affected by quality-drop note
Temporary safety caution factor for Climb ASP 1
Mountain capacity reduction after bad weather
Higher repeat-visit penalty for Climb
```

---

## Constraints

Create dynamic controls for:

```text
ASP capacity limits
Weather/security risk
Skills and certifications
Field activity budget
Safety threshold for Climb
Concentration risk cap
Minimum eligible ASP share
```

Default values:

```text
Monthly field activity budget: 180000
Maximum ASP share per profile: 60%
Minimum eligible ASP share: 10%
Climb safety threshold: 90
Weather impact active: true
SME adjustment layer active: true
```

If an ASP is not certified for Climb or below Climb safety threshold, allocate zero Climb tasks to that ASP.

---

## Allocation Engine

Recommend task-volume split by profile and ASP.

Output should be both percentages and task counts.

Use constrained optimization if available.

If a solver package is not available, implement a greedy constrained allocation algorithm:

```text
1. Remove ineligible ASPs.
2. Apply SME-driven caps.
3. Apply minimum shares where feasible.
4. Sort eligible ASPs by business score.
5. Allocate remaining demand to highest-score ASPs until capacity, budget, safety, certification, max share and SME caps are reached.
6. If demand cannot be fully allocated, return infeasible status and explain blockers.
```

The recommendation must include reason codes.

---

## Recommendation Tab

Show:

```text
Recommended allocation for next 4 weeks
Stacked horizontal bar chart by profile
Current vs recommended KPI cards
Reason codes for each ASP
Infeasibility explanation if applicable
```

KPIs to show:

```text
Average cost per task
SLA compliance
NPS
Repeat visit rate
Safety risk index
Budget usage
Certified capacity coverage
```

Do not show time of delivery as a KPI.

---

## Scenarios

Implement scenario buttons:

```text
Balanced Mode
Cost Pressure
SLA Recovery
Bad Mountain Weather
Climb Certification Issue
Next Month Rebalance
```

Scenario behavior:

### Balanced Mode

Reset weights and constraints to default values.

### Cost Pressure

Reduce budget by 15% and increase cost weight.

### SLA Recovery

Increase SLA weight and reduce allocation to low-SLA ASPs.

### Bad Mountain Weather

Set Mountain weather risk to High and reduce Mountain capacity.

### Climb Certification Issue

Remove Climb certification from one Climb ASP and rerun allocation.

### Next Month Rebalance

Update ASP performance:

```text
One ASP deteriorates: lower SLA and higher repeat visits
One ASP improves: higher safety and lower repeat visits
```

Then rerun allocation with dynamic rebalancing.

---

## Technical Details Expanders

Each tab should include an optional expander called:

```text
Technical Details
```

Technical details to include:

```text
Business Scorecard = multi-criteria decisioning
Data Confidence = Bayesian smoothing / probabilistic reasoning
Causal Intelligence = causal inference and SME-informed assumptions
Allocation Engine = constrained optimization
Management Simulator = what-if simulation and adaptive learning
```

Mention production methods only inside expanders:

```text
Weighted scoring
MCDA
TOPSIS
AHP
Bayesian smoothing
Hierarchical Bayesian models
Bayesian networks
Causal graphs
Propensity score adjustment
Doubly robust estimation
Causal forests
Linear programming
Mixed-integer programming
Robust optimization
Stochastic optimization
Contextual bandits
Reinforcement learning
Markov decision processes
Agentic orchestration
```

---

## Visual Style

Use:

```text
KPI metric cards
Stacked horizontal allocation bars
Grouped bar charts
Traffic-light status labels
Sticky-note style SME cards
Before/after comparison
Scenario result cards
Timeline for dynamic rebalancing
```

Color semantics:

```text
Green: good / feasible / improved
Amber: caution / medium confidence / watch item
Red: risk / violation / infeasible
Blue: neutral business information
Purple: prescriptive engine layer
```

---

## Tests

Create unit tests for:

```text
Data generator creates required columns
Missing values are generated intentionally
Smoothing produces stable values
Scores are between 0 and 100
Climb ineligible ASP receives zero tasks
Budget constraint is respected
Capacity constraint is respected
SME caps are respected
Infeasibility is detected
Scenario changes recommendation
Time of delivery is not part of KPI list
```

---

## Deliverables

Generate:

```text
app.py
requirements.txt
README.md
src/ modules
tests/ modules
config files if useful
```

The app must run with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Final Demo Message

The app should close with:

```text
Today we often report what happened. With prescriptive analytics, we recommend what to do next.
```
