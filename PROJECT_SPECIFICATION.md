# Dynamic Allocation Optimizer — Project Specification

## 1. Overview

A Streamlit-based prescriptive analytics demo that recommends how to split field-service task volume across Authorized Service Providers (ASPs) for three profiles: Urban, Mountain, and Climb.

**Run:** `pip install -r requirements.txt && streamlit run app.py`

---

## 2. Architecture

```
app.py (Streamlit UI, ~1700 lines)
├── src/
│   ├── data_generator.py    — synthetic task-level data generation
│   ├── data_quality.py      — Bayesian smoothing + winsorization
│   ├── scoring.py           — multi-criteria weighted scoring (global normalization)
│   ├── causal_layer.py      — causal adjustment + SME delta scoring
│   ├── sme_layer.py         — structured SME observations
│   ├── constraints.py       — constraint builder (capacity, weather, skills, budget)
│   ├── optimizer.py         — score²-proportional constrained allocator
│   ├── scenarios.py         — scenario template loader
│   ├── explanations.py      — reason code generator
│   └── visualization.py     — Plotly chart helpers
├── config/
│   ├── default_settings.yaml
│   └── scenario_templates.yaml
├── tests/
│   └── test_demo.py
├── DEMO_TYPESCRIPT.md        — 45-min presentation script
├── CURRENT_STATE.md          — technical state documentation
└── requirements.txt
```

---

## 3. Tabs (12)

| # | Tab | Purpose | Key Interaction |
|---|-----|---------|-----------------|
| 1 | Demo Scope | Generic prescriptive analytics intro, 9-capability DI flow | Progressive reveal (3 clicks) |
| 2 | Use Case | Telco ASP problem statement, 3 profiles, baseline equal split | Progressive reveal (2 clicks) |
| 3 | Setup | Hyperparameters, synthetic data generation, volume forecasting | Generate button |
| 4 | Data Confidence | Bayesian smoothing, winsorization, missing/outlier handling | Show improvements button |
| 5 | Business Priorities | Weight sliders (must sum to 100%), radar charts, ASP ranking | Update Scores button |
| 6 | Causal Intelligence | Raw vs adjusted scores, SME observations, ranking flip | Progressive reveal (3 clicks) |
| 7 | Constraints | Capacity, weather, skills, budget, max/min share, rework caps | Apply Constraints button |
| 8 | Recommendation | Score²-proportional allocation, KPI delta vs equal split | Generate Split → Show KPI buttons |
| 9 | Dynamic Rebalancing | 36-month animated simulation with 3 annual events | Start Simulation → Play |
| 10 | Scenarios | 3 what-if scenarios with resilience scoring | Scenario buttons |
| 11 | Engine View | 10-capability table (demo vs production methods) | Static |
| 12 | Closing | Final statement | Static |

---

## 4. ASPs

| Profile | ASP 1 | ASP 2 | ASP 3 | Characteristics |
|---------|-------|-------|-------|-----------------|
| Urban | CityConnect | UrbanLink | StreetNet | Cheapest / Best SLA+NPS / Balanced |
| Mountain | AlpineReach | SummitField | AlpinGmbH | Best quality (low repeat) / Cheapest+safest / Best SLA |
| Climb | SkyClimb | TowerPro | VerticalWorks | Cheap but risky / Best SLA+NPS / Safest, most expensive |

All ASPs operate across the entire country (overlapping geography).

---

## 5. Data Generation

- **Input:** seed, total volume, variance (0.1–1.0), historical weeks, planning weeks
- **Output:** task-level DataFrame (26 columns) with intentional quality issues (missing NPS ~18%, outliers, sparse safety events, assignment bias)
- **Forecasting:** `avg_weekly × planning_weeks × (1 + 0.02 × planning_weeks)`
- **Budget:** scales with forecasted volume × cost/task × 1.2 headroom

---

## 6. Scoring & Optimization

### Scoring
- Global normalization (min-max across all 9 ASPs)
- KPIs: Cost (inverse), Safety, SLA, NPS, Repeat (inverse)
- Weighted by Business Priorities sliders (must sum to 100%)
- Causal adjustment applied as delta to Mountain ASPs (once)

### Optimizer
1. Initial allocation proportional to score²
2. Winner bonus: +8% top ASP, +3% second, -11% last
3. Constraint clipping: min 15%, max 60%, capacity, SME caps
4. Reconciliation: redistribute surplus/deficit by score rank

---

## 7. Causal Intelligence

- **Data ratios:** complexity, travel, weather, access (relative to profile average)
- **Formula:** `adjustment = 18×(complexity_ratio-1) + 8×(travel_ratio-1) + 6×(weather_ratio-1) + 6×(access_ratio-1)`
- **SME effects:** emergency expertise (+10), max share cap (-3), flood penalty (-8)
- **Applied once** per data generation (tracked by `causal_applied` flag)

---

## 8. Constraints

| Constraint | Default |
|------------|---------|
| Min share per ASP | 15% |
| Max share per ASP | 60% |
| Budget | Auto-scaled with volume |
| Skills (Urban) | min 10% Sr / min 60% Reg / max 30% Jr |
| Skills (Mountain) | min 30% Sr / min 60% Reg / max 10% Jr |
| Skills (Climb) | min 50% Sr / min 40% Reg / max 10% Jr |
| Rework cap (Mountain) | 10% |
| Rework cap (Climb) | 5% |
| Weather | Simulated forecast per profile |
| Climb safety | Mandatory gate (100%) |

---

## 9. Dynamic Rebalancing (36 months)

| Period | Event | Effect |
|--------|-------|--------|
| M6–M10 | UrbanLink & VerticalWorks internal capacity issue | Capped at 25% |
| M18–M21 | Flood hits Urban & Climb (2 districts) | SLA/NPS collapse, cost +€15, Mountain unaffected |
| M25+ | Network rollout | First ASPs exit, new ASPs (4, 5) enter |

- Movement cap: 5pp/month
- Max share: from Constraints tab
- KPIs: deterministic per month (seeded RNG)
- NPS: starts negative (~-25), trends to +35, collapses during flood

---

## 10. What-If Scenarios

| Scenario | Levels | Key Change | Resilience Range |
|----------|--------|------------|-----------------|
| 💰 Budget Reduction | -5%, -15%, -25% | Cost weight increases, budget drops | 65–77 |
| 📈 Demand Increase | +10%, +20%, +40% | Volume scales, capacity bites | 80–89 |
| 📡 4G→5G Swap | Conservative, Expected, Accelerated | First ASPs penalized/removed, new ASPs enter, cost +48% | 88–95 |

Each shows: Baseline vs 2 levels side-by-side, traffic-light trade-off boxes, resilience score, actionable recommendations.

---

## 11. SME Observations

| # | Role | ASP | Observation | Engine Effect |
|---|------|-----|-------------|---------------|
| 1 | Safety Manager | SkyClimb | Changed supervisors, lower operational confidence | Temporary safety caution (max 25% Climb) |
| 2 | Dispatcher | AlpineReach | Handles hardest emergency escalations | +10 score boost |
| 3 | Operations Manager | AlpineReach | Quality drops above 45% share (subcontractors) | Max share cap 45% |
| 4 | Contract Manager | — (Climb) | Repeat visits have greater reputational impact | 1.5× repeat penalty |
| 5 | Regional Expert | AlpinGmbH | Flooding in 2 districts last quarter caused delays | -8 score penalty |

---

## 12. UI Design Principles

- **Progressive reveal:** sections appear on click (Demo Scope, Use Case, Causal Intelligence)
- **Button-gated outputs:** charts/results only after explicit action
- **Amber italic summaries:** centered quote at the end of each tab (after last interaction)
- **Colors:** ASP1=green, ASP2=blue, ASP3=red, ASP4=orange, ASP5=purple
- **Data flow:** left-to-right through tabs; session state carries data downstream
- **Deterministic:** seeded RNG everywhere; Play always gives same results

---

## 13. Decision Intelligence Framework (9+1 capabilities)

| # | Capability | Demonstrated |
|---|-----------|--------------|
| 📊 | Decision Value Model | ✅ Business Priorities + Scoring |
| 🧹 | Uncertainty & Data Reliability | ✅ Data Confidence |
| 🧠 | Causal / Driver Intelligence | ✅ Causal Intelligence |
| 🎯 | Prescriptive Optimization | ✅ Recommendation |
| ⏱️ | Adaptive Policy / Rebalancing | ✅ Dynamic Rebalancing |
| 🤖 | Reinforcement Learning | ⚠️ Simplified (production: Offline RL, Thompson Sampling) |
| 🧪 | Scenario & Risk Simulation | ✅ Scenarios |
| 💬 | Decision Explanation | ✅ Reason codes |
| 🛡️ | Governance & Decision Rights | ⚠️ Conceptual (constraints = hard gates) |
| 🔁 | Outcome Learning | ⚠️ Conceptual (rebalancing score updates) |

---

## 14. Technology Stack

- Python 3.11+
- Streamlit ≥1.28
- Pandas, NumPy
- Plotly ≥5.15
- SciPy, PuLP (available but not required — greedy allocator used)
- PyYAML
- Pytest

---

## 15. Demo Presentation

- **Duration:** 45 minutes
- **Script:** `DEMO_TYPESCRIPT.md`
- **Recommended seed:** 42 (good causal flip), 1780 (strongest Mountain flip)
- **Flow:** Always left-to-right. Generate data → Update scores → Apply constraints → Generate split
- **Role:** Decision Intelligence Lead
