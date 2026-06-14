# Dynamic ASP Allocation Optimizer
## Business Specification for Prescriptive Analytics Demo in Telco Field Services

> Purpose: this file defines the business-focused demo specification. It is designed to be used as input for Kiro-cli or another coding agent to generate an interactive Python demo.

---

## 1. Demo Purpose

Build a simple, visual, business-friendly demo showing how prescriptive analytics helps a telco company decide:

> **How should we split field-service task volume across ASPs, considering cost, safety, SLA, NPS, repeat visits, capacity, weather/security risk, certifications, budget, data quality, causal context, and SME knowledge?**

The demo must be easy to understand for non-technical stakeholders. Technical details must be hidden by default and available only in expandable sections.

---

## 2. Target Audience

The demo is for mixed stakeholders:

- Business executives
- Field operations managers
- Contract managers
- Safety/security managers
- Product managers
- Analytics/data science teams
- Procurement/vendor management teams

The default UI must use simple business language.

Avoid technical jargon on the main screens. Use terms like:

- **Business Scorecard** instead of multi-criteria decisioning
- **Data Confidence Layer** instead of Bayesian smoothing
- **Causal Intelligence Layer** instead of causal inference
- **Allocation Engine** instead of constrained optimization
- **Management Simulator** instead of scenario simulation/adaptive learning

---

## 3. Core Business Story

Today, field-service allocation is often based on:

- Static allocation rules
- Manual judgment
- Historical ASP performance
- Limited KPI dashboards
- Contractual minimums
- Escalation-driven allocation decisions

The demo should show a better future:

> The system generates realistic operational data, improves imperfect data, adds SME knowledge, applies business priorities and constraints, and recommends a practical task-volume split across ASPs.

---

## 4. Field-Service Scope

There are three service profiles.

| Profile | Business Meaning | Main Challenge |
|---|---|---|
| Urban | Standard city field tasks | High volume, cost, SLA, NPS |
| Mountain | Standard tasks with difficult travel | Weather, access, delays, SLA risk |
| Climb | Risky climbing work | Safety, certifications, skills |

Each profile has three ASPs:

```text
Urban:    Urban ASP 1, Urban ASP 2, Urban ASP 3
Mountain: Mountain ASP 1, Mountain ASP 2, Mountain ASP 3
Climb:    Climb ASP 1, Climb ASP 2, Climb ASP 3
```

---

## 5. KPIs Used in the Demo

The demo must use the following KPIs.

| KPI | Direction | Business Meaning |
|---|---:|---|
| Cost per task | Lower is better | Field delivery cost, including direct delivery cost and operational overhead assumptions |
| Safety / Security score | Higher is better | Safety compliance, incidents, certification coverage, weather/security exposure |
| SLA compliance | Higher is better | Percentage of tasks completed within contractual SLA |
| NPS | Higher is better | Customer satisfaction after completed visits |
| Repeat visit rate | Lower is better | Percentage of tasks requiring follow-up visits due to incomplete or failed fix |
| Budget usage | Lower or within limit | Total planned cost versus available field activity budget |
| Certified capacity coverage | Higher is better | Available certified workforce versus required profile-specific demand |

Important: **do not include time of delivery as a KPI** in this demo.

---

## 6. Five Prescriptive Analytics Capabilities to Demonstrate

Use these five business-friendly capability names in the UI.

| # | Business Name | What It Shows | Technical Method Hidden by Default |
|---:|---|---|---|
| 1 | Business Scorecard | ASP comparison across cost, safety, SLA, NPS and repeat visits | Multi-criteria decisioning |
| 2 | Data Confidence Layer | Useful decisions despite noisy/incomplete data | Bayesian smoothing, probabilistic reasoning |
| 3 | Causal Intelligence Layer | Why raw KPIs may be misleading | Causal inference, counterfactual reasoning |
| 4 | Allocation Engine | Recommended feasible task-volume split | Constrained optimization |
| 5 | Management Simulator | Scenarios and dynamic rebalancing over time | What-if simulation, adaptive learning |

---

## 7. Demo Duration and Flow

The demo must support a 45-minute walkthrough.

| Time | Section | Business Message |
|---:|---|---|
| 0–5 min | Business context | Static allocation cannot handle operational complexity |
| 5–9 min | Generate data | We create realistic imperfect data |
| 9–14 min | Data confidence | Imperfect data can still support decisions |
| 14–20 min | Business scorecard | “Best ASP” depends on company priorities |
| 20–27 min | Causal intelligence | Raw KPIs can be misleading without context |
| 27–34 min | Allocation engine | Recommend feasible volume split |
| 34–40 min | Scenarios | Test budget, weather, certification and SLA pressure |
| 40–44 min | Dynamic rebalancing | Allocation adapts over time |
| 44–45 min | Wrap-up | Prescriptive analytics recommends what to do next |

---

## 8. User Experience Principle

The demo should feel like a **management cockpit**, not a technical notebook.

Use:

- Visual cards
- Simple icons
- Charts
- Traffic-light colors
- Short explanations
- Expandable technical sections
- Clear reason codes
- Before/after comparison
- Scenario buttons
- Stacked allocation bars

Avoid:

- Dense tables as the primary view
- Too many formulas
- Technical jargon on the main screen
- Data-science-heavy presentation by default

---

## 9. Recommended Screen Structure

The app should have seven main screens or sections.

```text
1. Demo Setup
   Generate synthetic field-service world

2. Data Confidence
   Show missing/noisy data and corrected usable view

3. Business Priorities
   OKR vs contractual goal sliders

4. Causal Intelligence
   Explain why raw KPI ranking can be misleading

5. Constraints
   Capacity, weather/security, certifications, budget, safety

6. Recommendation
   Recommended ASP task-volume split

7. Scenarios and Dynamic Rebalancing
   What-if and time simulation
```

---

## 10. Screen 1 — Demo Setup

### Purpose

Let the presenter create a fresh synthetic telco field-service world.

### Main UI

```text
┌─────────────────────────────────────────────────────────────┐
│ Dynamic ASP Allocation Optimizer                            │
│ Telco Field Services Prescriptive Analytics Demo            │
├─────────────────────────────────────────────────────────────┤
│ Profiles: Urban | Mountain | Climb                         │
│ ASPs per profile: 3                                        │
│ Planning period: Next 4 weeks                              │
│                                                             │
│ [ Generate Synthetic Data ]                                │
│ [ Reset Demo ]                                             │
└─────────────────────────────────────────────────────────────┘
```

### After data generation, show cards

```text
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Urban Demand  │ │ Mountain      │ │ Climb Demand  │
│ 1,200 tasks   │ │ 420 tasks     │ │ 160 tasks     │
└───────────────┘ └───────────────┘ └───────────────┘

┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Data Quality  │ │ Budget        │ │ Weather Risk  │
│ Medium        │ │ €180,000      │ │ Moderate      │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## 11. Synthetic Data Requirements

The demo must generate task-level data dynamically.

Each generated task should include:

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

The dataset must intentionally include:

- Missing values
- Small sample sizes
- Noise
- Outliers
- Biased assignment patterns
- Undocumented operational context
- Different task difficulty by ASP
- Weather/security impact
- Certification limitations

---

## 12. Screen 2 — Data Confidence Layer

### Purpose

Show that prescriptive analytics can work with medium-quality, incomplete data.

### Main UI

```text
┌─────────────────────────────────────────────────────────────┐
│ Data Confidence Layer                                       │
│ “We do not wait for perfect data. We make imperfect data     │
│ decision-ready.”                                            │
├─────────────────────────────────────────────────────────────┤
│ Missing NPS values:              18%                        │
│ Low sample ASP metrics:          27%                        │
│ Outliers detected:               9                          │
│ Safety data sparsity:            High                       │
│ Overall data confidence:         Medium                     │
└─────────────────────────────────────────────────────────────┘
```

### Required visual

```text
Before Processing                After Processing
┌───────────────┐                ┌───────────────┐
│ Missing data  │  ───────────▶  │ Imputed data  │
│ Noisy metrics │                │ Smoothed KPIs │
│ Small samples │                │ Confidence    │
└───────────────┘                └───────────────┘
```

### Example mini-table

| Profile | ASP | Raw NPS | Responses | Smoothed NPS | Confidence |
|---|---:|---:|---:|---:|---|
| Mountain ASP 1 | Mountain | 65 | 4 | 51 | Low |
| Mountain ASP 2 | Mountain | 52 | 80 | 52 | High |
| Mountain ASP 3 | Mountain | 48 | 18 | 49 | Medium |

### Business explanation

Display this text:

> “If an ASP has only a few responses, the engine avoids overreacting. It adjusts weak data toward a reasonable baseline and tracks confidence.”

### Hidden technical details

Place in an expandable panel.

```text
Technical Details

Method:
Bayesian smoothing / empirical Bayes style adjustment.

Purpose:
Reduce overreaction to small samples and noisy operational data.

Production considerations:
- Use hierarchical smoothing by profile, region, ASP and task type.
- Track confidence intervals.
- Separate missing-at-random from systematic missingness.
- Monitor data drift and quality degradation.
```

---

## 13. Screen 3 — Business Priorities

### Purpose

Let stakeholders set what the company cares about today.

### Main UI

```text
┌─────────────────────────────────────────────────────────────┐
│ Business Priorities                                         │
├─────────────────────────────────────────────────────────────┤
│ Company OKRs              Contractual Goals                 │
│ Cost + Safety             SLA + NPS + Repeat Visits         │
│                                                             │
│ OKR Importance:           [██████████----------] 50%        │
│ Contractual Importance:   [██████████----------] 50%        │
└─────────────────────────────────────────────────────────────┘
```

### Expanded sliders

```text
Company OKRs
Cost                  [██████--------------] 30%
Safety/Security       [████████████--------] 70%

Contractual Goals
SLA                   [████████------------] 45%
NPS                   [██████--------------] 35%
Repeat Visits         [████----------------] 20%
```

### Business explanation

Display:

> “The definition of the best ASP changes depending on business priorities. The demo lets stakeholders change priorities and immediately see the impact.”

### Hidden technical details

```text
Technical Details

Method:
Multi-criteria decisioning.

Possible production methods:
- Weighted scoring
- Multi-criteria decision analysis
- TOPSIS
- Analytic hierarchy process
- Rule-based score modifiers

Production considerations:
- Normalize metrics carefully.
- Use separate scoring logic by profile.
- Treat safety for Climb as a hard constraint, not only a weighted score.
- Store priority templates such as Cost Mode, SLA Mode, Safety Mode.
```

---

## 14. Screen 4 — Causal Intelligence Layer

### Purpose

Show the effect of causal inference.

The audience should understand:

> Raw KPI ranking can be misleading because ASPs may receive different types of work.

### Main screen title

```text
Causal Intelligence Layer
“Do we know who performs better — or just who received easier work?”
```

### Visual 1 — Naive KPI ranking

```text
Raw Mountain SLA Ranking

ASP 1  ████████████████░░░░ 84%
ASP 2  ██████████████████░░ 92%
ASP 3  █████████████████░░░ 88%
```

Initial business interpretation:

```text
ASP 2 looks best.
ASP 1 looks weak.
```

### Visual 2 — Reveal task context

```text
Task Difficulty Mix

                Complexity   Travel Difficulty   Emergency Share
ASP 1           High         High                38%
ASP 2           Medium       Medium              12%
ASP 3           Medium       High                20%
```

Updated business interpretation:

```text
ASP 1 receives harder work.
Raw SLA alone is not a fair comparison.
```

### Visual 3 — SME observation sticky notes

```text
┌─────────────────────────────────────────────────────────────┐
│ SME Observation                                             │
│ Dispatcher: “Mountain ASP 1 is often used for difficult      │
│ emergency jobs because they know the region best.”           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SME Observation                                             │
│ Operations Manager: “ASP 1 quality drops when share exceeds  │
│ 45% because they rely more on subcontractors.”               │
└─────────────────────────────────────────────────────────────┘
```

### Visual 4 — Recommendation after causal context

```text
Naive decision:
Reduce ASP 1 volume.

Causal decision:
Keep ASP 1 for difficult emergency Mountain tasks,
but cap total Mountain share at 45%.
```

### SME knowledge must affect the recommendation

| SME Insight | Engine Effect |
|---|---|
| ASP quality drops above 45% share | Cap ASP max share at 45% |
| ASP recently changed supervisors | Temporary safety caution factor |
| ASP receives harder jobs | Adjust KPI comparison for complexity |
| ASP completed new training | Allow controlled gradual volume increase |
| Certain roads unsafe after rain | Reduce Mountain capacity during bad weather |

### Hidden technical details

```text
Technical Details

Method:
Causal inference and expert-informed causal reasoning.

Purpose:
Avoid rewarding or penalizing ASPs based only on raw historical KPIs.

Possible production methods:
- Causal graphs
- Counterfactual analysis
- Propensity score adjustment
- Treatment effect estimation
- Difference-in-differences
- Causal forests
- Human-in-the-loop causal assumptions

Production considerations:
- Capture treatment/assignment policy variables.
- Track task complexity.
- Track assignment bias.
- Separate ASP performance from task difficulty.
- Store SME observations as structured assumptions with expiry date and confidence level.
```

---

## 15. Screen 5 — Constraints

### Purpose

Let the audience dynamically change operational constraints.

The recommendation must react immediately.

### Main UI

```text
┌─────────────────────────────────────────────────────────────┐
│ Operational Constraints                                     │
├─────────────────────────────────────────────────────────────┤
│ ASP Capacity Limits                 ON                     │
│ Weather / Security Risk             ON                     │
│ Skills & Certifications             ON                     │
│ Field Activity Budget               ON                     │
│ Safety Threshold for Climb          ON                     │
│ Concentration Risk Cap              ON                     │
└─────────────────────────────────────────────────────────────┘
```

### Required dynamic constraints

#### ASP capacity

```text
Urban ASP 2 max capacity: 520 tasks
Mountain ASP 1 max capacity: 140 tasks
Climb ASP 3 max capacity: 90 tasks
```

#### Weather/security

```text
Mountain weather risk: High
Effect: reduce Mountain field capacity by 20%
```

```text
Regional security restriction: Active
Effect: only ASPs with approved security protocol may receive tasks
```

#### Skills and certifications

```text
Climb task requirements:
- Height-work certification
- Valid safety training
- Minimum certified technician availability
- Valid insurance
```

If not met:

```text
ASP receives 0 Climb tasks.
```

#### Budget

```text
Monthly field activity budget: €180,000
```

The allocation must stay within budget or clearly tell the user the plan is infeasible.

#### Safety threshold

```text
Minimum Climb safety score: 90/100
```

#### Concentration risk

```text
No ASP can receive more than 60% of one profile volume.
```

### Business explanation

Display:

> “The engine does not simply choose the best ASP. It chooses the best feasible allocation.”

### Hidden technical details

```text
Technical Details

Method:
Constrained optimization.

Possible production methods:
- Linear programming
- Mixed-integer programming
- Goal programming
- Robust optimization
- Stochastic optimization
- Constraint programming

Production considerations:
- Separate hard constraints from soft preferences.
- Safety and certification should be hard constraints for Climb.
- Infeasibility should be explained clearly.
- Allow override workflow with approval.
- Keep a full audit trail of constraints and recommendations.
```

---

## 16. Screen 6 — Recommendation

### Purpose

Show the prescriptive answer.

Not a ranking. Not a dashboard. A concrete allocation recommendation.

### Main UI

```text
Recommended Allocation for Next 4 Weeks
```

Example:

| Profile | ASP 1 | ASP 2 | ASP 3 |
|---|---:|---:|---:|
| Urban | 30% | 50% | 20% |
| Mountain | 35% | 45% | 20% |
| Climb | 5% | 35% | 60% |

### Visual

Use stacked horizontal bars.

```text
Urban
ASP 1 ██████████ 30%
ASP 2 █████████████████ 50%
ASP 3 ███████ 20%

Mountain
ASP 1 ████████████ 35%
ASP 2 ███████████████ 45%
ASP 3 ██████ 20%

Climb
ASP 1 ██ 5%
ASP 2 ████████████ 35%
ASP 3 ███████████████████ 60%
```

### Show expected impact

```text
┌──────────────────────┐ ┌──────────────────────┐
│ Cost per task         │ │ SLA compliance        │
│ €112 → €106           │ │ 87% → 92%             │
│ Improved              │ │ Improved              │
└──────────────────────┘ └──────────────────────┘

┌──────────────────────┐ ┌──────────────────────┐
│ NPS                   │ │ Repeat visits         │
│ 43 → 49               │ │ 9.5% → 6.8%           │
│ Improved              │ │ Improved              │
└──────────────────────┘ └──────────────────────┘
```

### Reason codes

Each recommendation must include simple explanation cards.

```text
Mountain ASP 1: 35%
+ Handles difficult emergency jobs well
+ Strong regional knowledge
- Raw SLA looks weaker due to harder task mix
- Capped at 45% because quality drops at high volume
```

```text
Climb ASP 3: 60%
+ Best safety score
+ Strongest certified workforce
+ Lowest repeat visit rate
- Capacity close to limit
```

```text
Urban ASP 2: 50%
+ Strong SLA
+ Best NPS
+ Enough available capacity
- Higher cost than ASP 1
```

### Infeasibility message

If constraints cannot be satisfied, show:

```text
No feasible allocation found under current constraints.

Main blockers:
1. Climb certified capacity is insufficient.
2. Budget is too low for required volume.
3. Weather restriction reduces Mountain capacity below demand.

Suggested actions:
- Increase budget by €18,000, or
- Relax max ASP share from 60% to 70%, or
- Add certified Climb capacity.
```

---

## 17. Screen 7 — Scenarios and Dynamic Rebalancing

### Purpose

Show future-facing value.

The system should allow users to test scenarios and move time forward.

### Scenario buttons

```text
[ Balanced Mode ]
[ Cost Pressure ]
[ SLA Recovery ]
[ Bad Mountain Weather ]
[ Climb Certification Issue ]
[ Next Month Rebalance ]
```

### Scenario A — Cost Pressure

Input:

```text
Budget reduced by 15%
```

Expected behavior:

- More volume moves to cheaper ASPs.
- Safety and certifications remain hard constraints.
- Some SLA/NPS trade-off may be visible.

Message:

```text
Cost can be reduced, but not by violating critical safety rules.
```

### Scenario B — SLA Recovery

Input:

```text
SLA priority increases.
```

Expected behavior:

- More work moves to high-SLA ASPs.
- Expensive but reliable ASPs may win more volume.

Message:

```text
The system protects contractual performance when SLA risk rises.
```

### Scenario C — Bad Mountain Weather

Input:

```text
Mountain weather risk becomes High.
```

Expected behavior:

- Mountain capacity decreases.
- ASPs with better access reliability receive more work.
- Feasibility risk may be flagged.

Message:

```text
The system changes allocation before SLA is breached.
```

### Scenario D — Climb Certification Issue

Input:

```text
Climb ASP 2 loses required certification.
```

Expected behavior:

- Climb ASP 2 receives zero Climb allocation.
- Volume redistributes to certified ASPs.
- If capacity is insufficient, the system flags infeasibility.

Message:

```text
Safety is not a preference. It is a gate.
```

### Dynamic rebalancing

Show a timeline.

```text
Week 1 ─── Week 2 ─── Week 3 ─── Week 4 ─── Next Plan
```

Example:

```text
Mountain ASP 2:
SLA drops from 94% to 84%.
Repeat visits increase from 5% to 10%.

Recommended share:
55% → 35%
```

Example:

```text
Climb ASP 1:
Certification coverage improves.
Safety stabilizes.
Repeat visits decrease.

Recommended share:
5% → 15%, still capped until confidence improves.
```

---

## 18. Engine View

The demo must include an optional **Engine View**.

Default state: collapsed.

```text
┌─────────────────────────────────────────────────────────────┐
│ Engine View                                                 │
│ Hidden by default. Open only for technical audience.         │
├─────────────────────────────────────────────────────────────┤
│ 1. Generated synthetic data                                 │
│ 2. Data confidence processing                               │
│ 3. SME observations and causal assumptions                   │
│ 4. Constraints and engine settings                          │
│ 5. Optimized allocation output                              │
└─────────────────────────────────────────────────────────────┘
```

Use business-friendly labels.

```text
Data confidence strength: Medium
Recent performance weight: 70%
Historical baseline weight: 30%
Minimum confidence threshold: 40%
Maximum ASP share: 60%
Minimum eligible ASP share: 10%
Climb safety threshold: 90/100
Budget limit: €180,000
Weather impact: Active
SME adjustment layer: Active
```

---

## 19. Main Business KPIs for Current vs Recommended Allocation

Show these KPIs as cards:

```text
Average cost per task
SLA compliance
NPS
Repeat visit rate
Safety risk index
Budget usage
Certified capacity coverage
```

Example:

```text
Cost per task:              €112 → €106
SLA compliance:             87% → 92%
NPS:                        43 → 49
Repeat visits:              9.5% → 6.8%
Safety risk:                Medium → Low
Budget usage:               €179,000 / €180,000
Certified capacity coverage: 86% → 98%
```

---

## 20. Required Wow Moments

### Wow Moment 1 — Imperfect data becomes useful

```text
Raw NPS is unreliable because sample size is tiny.
The engine smooths it and shows confidence.
```

Message:

> “We do not need perfect data to begin making better decisions.”

### Wow Moment 2 — Raw KPI ranking is misleading

```text
ASP 1 looks weak on SLA.
Then we reveal ASP 1 receives harder emergency work.
The recommendation changes.
```

Message:

> “Historical data tells us what happened. Causal intelligence helps explain why.”

### Wow Moment 3 — Safety blocks cheap allocation

```text
Cost pressure increases.
Cheap ASP would normally get more work.
But Climb safety threshold blocks unsafe allocation.
```

Message:

> “Safety is not just a preference. It is a gate.”

### Wow Moment 4 — Infeasibility is valuable

```text
Bad weather + certification limits make Climb demand impossible.
The engine says no feasible allocation exists.
```

Message:

> “A good prescriptive system should tell us when the operating model cannot meet demand.”

---

## 21. Acceptance Criteria

The implementation is successful if:

1. The app can generate synthetic data dynamically.
2. The data includes missing values, noise, small samples and biased assignment.
3. The app shows a data confidence layer.
4. The app shows Bayesian-smoothed or confidence-adjusted metrics.
5. The app includes SME observations.
6. SME observations affect recommendations.
7. The app shows raw KPI ranking and adjusted causal interpretation.
8. The app supports dynamic business priority sliders.
9. The app supports dynamic constraints:
   - capacity
   - weather/security
   - certifications/skills
   - budget
   - safety threshold
10. The app recommends task-volume split by profile and ASP.
11. The app explains recommendations with reason codes.
12. The app supports what-if scenarios.
13. The app supports time-based dynamic rebalancing.
14. Technical methods are hidden by default.
15. Technical details can be expanded on demand.
16. Time of delivery is not used as a KPI.
17. The demo can be presented in 45 minutes.
18. The UI is simple and visual enough for non-technical stakeholders.

---

## 22. Final Demo Message

The demo should close with this message:

> “Prescriptive analytics is not just one algorithm. It is a decision capability. It combines business priorities, imperfect data, SME knowledge, causal reasoning, constraints, and simulation to recommend what the company should do next.”

Short version:

> “Today we often report what happened. With prescriptive analytics, we recommend what to do next.”
