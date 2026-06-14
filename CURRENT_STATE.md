# Dynamic ASP Allocation Optimizer — Current State

## Overview
Prescriptive analytics demo for telco field services. Recommends task-volume splits across ASPs for Urban, Mountain, and Climb profiles.

**Run:** `pip install -r requirements.txt && streamlit run app.py`

---

## Tabs (10 total)

### 1. Specification
Colorful overview: problem statement, audience, today vs tomorrow, 3 profiles, 5 capabilities.

### 2. Setup
**Hyperparameters:** Historical Task Volume, Data Variance (0.1–1.0), Historical Weeks, Planning Period, Random Seed.

- Generates synthetic task-level data (26 columns) with intentional quality issues
- Forecasts future volume: `(historical/hist_weeks) × plan_weeks × (1 + 0.02×plan_weeks)`
- Budget auto-scales with volume (130€ base - volume discount, +30% headroom)
- Shows historical vs forecasted volumes side-by-side

### 3. Data Confidence
Bayesian smoothing with winsorization (5th/95th percentile). Shows:
- Missing NPS (stacked bar), Outlier handling (histogram overlay), NPS smoothing (grouped bar)
- Per-ASP confidence table
- Technical details explain the exact method

### 4. Business Priorities
- Weight sliders: Cost, Safety, SLA, NPS, Repeat Visits (must sum to 100%)
- "Update Scores" button triggers recalculation
- Per-profile: Ranking (🥇🥈🥉) | Radar chart (ASP1=green, ASP2=blue, ASP3=red) | KPI score table
- Scoring normalized globally across all 9 ASPs

### 5. Causal Intelligence
Two-step analysis on Mountain profile:
- **Step 1 (Data):** Adjusts scores using complexity_ratio, travel_ratio, weather_ratio, access_ratio
- **Step 2 (SME):** Dispatcher (emergency expertise +10), Ops Manager (quality cap -3), Regional Expert (event penalty on ASP3 -8)
- Updates `scored` dataframe with causal adjustments (deltas applied)
- Conclusions show ranking flip with data-driven text

### 6. Constraints
- Toggles: Capacity, Weather/Security, Skills & Certifications
- Inputs: Budget, Max Rework Rate, Max ASP Share
- Weather forecast simulated based on planning period + seed
- Workforce: senior/regular/junior % per ASP
- "Apply Constraints" button activates settings
- Shows per-profile limits (capacity, weather reduction, certification gates)

### 7. Recommendation
- Optimizer: proportional to score² + winner bonus (+15% top, +5% second, -20% last)
- Constraints applied: max_share, capacity×(plan_weeks/4), weather reduction, SME caps
- Shows: Stacked bar (Urban top, Climb bottom), Aggregated KPI impact vs equal 1/3
- Detail expander: per-profile ASP cards + KPI delta + active constraints

### 8. Dynamic Rebalancing
36-month simulation starting from Recommendation output:
- **M6–M10:** ASP 1 hard-capped at 30%
- **M18–M21:** Flood hits all ASPs
- **M25+:** Network rollout — ASP 1 disappears, ASP 4 & ASP 5 enter
- ▶️ Play animates month-by-month (event banner + KPIs + allocation bar)
- Detail expander: 5 per-ASP line charts (Cost, SLA, NPS, Repeat, Allocation)
- 5pp/month movement cap, 70% max share, NPS range -40 to +35 with positive trend

### 9. Scenarios
Pre-built scenario buttons: Balanced, Cost Pressure, SLA Recovery, Bad Weather, Certification Issue, Next Month Rebalance.

### 10. Engine View
Technical reference: all settings, raw data sample, closing message.

---

## Data Flow

```
Setup (generate) → Data Confidence (smooth) → Business Priorities (score)
    → Causal Intelligence (adjust Mountain scores) → Constraints (apply)
        → Recommendation (optimize) → Dynamic Rebalancing (simulate 36 months)
```

Session state keys: `df`, `metrics`, `scored`, `demands`, `budget`, `constraint_settings`, `result`, `planning_weeks`, `workforce`

---

## Key Design Decisions

- **NPS range:** -100 to +100 (proper NPS scale)
- **Scoring:** Global normalization across all 9 ASPs (min-max 0–100)
- **Causal adjustment:** Applied as delta to business_score, not replacement
- **Optimizer:** Score² proportional + winner bonus, then constraints clip
- **Consistency:** Scores flow left-to-right; causal tab updates scored for downstream use
- **ASP colors:** ASP1=green, ASP2=blue, ASP3=red, ASP4=orange, ASP5=purple

---

## ASP Templates (base characteristics)

| ASP | Cost | SLA Rate | NPS Mean | Repeat | Safety | Complexity Bias | Emergency |
|-----|------|----------|----------|--------|--------|-----------------|-----------|
| Urban 1 | 75 | 0.86 | -10 | 10% | 80 | 0.35 | 8% |
| Urban 2 | 125 | 0.95 | 35 | 4% | 88 | 0.50 | 12% |
| Urban 3 | 100 | 0.82 | -15 | 13% | 76 | 0.70 | 6% |
| Mountain 1 | 120 | 0.87 | 35 | 6% | 75 | 0.85 | 45% |
| Mountain 2 | 100 | 0.93 | 5 | 4% | 90 | 0.35 | 8% |
| Mountain 3 | 140 | 0.84 | -10 | 12% | 82 | 0.50 | 18% |
| Climb 1 | 130 | 0.78 | -5 | 14% | 70 | 0.75 | 20% |
| Climb 2 | 170 | 0.91 | 20 | 5% | 93 | 0.40 | 8% |
| Climb 3 | 200 | 0.93 | 25 | 3% | 97 | 0.50 | 6% |

---

## SME Observations

1. Safety Manager: Climb ASP 1 changed supervisors (temporary caution)
2. Dispatcher: Mountain ASP 1 handles emergency jobs (expertise boost)
3. Ops Manager: Mountain ASP 1 quality drops >45% share (cap)
4. Contract Manager: Climb repeat visits have greater reputational impact
5. Regional Expert: Major event in ASP 3 regions next 2 weeks (penalty)

---

## Demo Presentation Tips

- Use seed=42 (default) or seed=1780 (stronger causal flip)
- Always regenerate data after changing Setup params
- Always click "Update Scores" after changing weights
- Always click "Apply Constraints" after changing constraints
- Visit tabs left-to-right for consistent data flow
- For cost demo: set Cost=100% weights → cheapest ASP dominates
- For safety demo: set Safety=100% → safest Climb ASP wins
