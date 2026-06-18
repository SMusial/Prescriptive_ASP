# Selected What-if Scenarios Specification
## Dynamic ASP Allocation Optimizer — Telco Field Services Demo

> Purpose: this file summarizes the four selected what-if scenarios for the telco field-services prescriptive analytics demo. It is designed as input for Kiro-cli or another code-generation agent.

---

## 1. Overview

The What-if Scenarios module should help stakeholders understand how robust the recommended ASP allocation is when business, operational, contractual or technology conditions change.

The selected scenarios are:

1. **Budget Reduction**
2. **Demand Increase**
3. **Repeat Visits Become Contractually Penalized**
4. **Network Swap from 4G to 5G**

These scenarios should demonstrate four types of value:

```text
Budget Reduction      → financial resilience
Demand Increase       → operational scalability
Repeat Visit Penalty  → quality and contract protection
4G to 5G Swap         → strategic transformation readiness
```

Main demo message:

> What-if scenarios help leadership see not only the best allocation for today, but how resilient that allocation is when cost, demand, quality expectations or network technology change.

Important KPI rule:

```text
Do not use time of delivery as a KPI in this demo.
```

---

# Scenario 1 — Budget Reduction

## Demo Message

```text
Can we reduce field-service cost without breaking SLA, safety, NPS or repeat-visit performance?
```

## KPIs to Observe

- Average cost per task
- Budget usage
- SLA compliance
- NPS
- Repeat visit rate
- Safety risk index
- Feasibility status

## Expected Insight

The demo should show the point where cost reduction is still acceptable — and where it becomes operationally or contractually risky.

Example interpretation:

```text
5–10% budget reduction: may be feasible.
15% budget reduction: may be feasible with warnings.
25% budget reduction: may create SLA risk, repeat visits, safety risk or infeasibility.
```

The goal is to show that the cheapest allocation is not always the safest or most resilient allocation.

## Uncertainty Management

Show budget sensitivity as a range:

```text
Mild cut:      -5%
Expected cut:  -15%
Severe cut:    -25%
```

For each level, the system should show:

- Whether the allocation remains feasible
- Whether SLA risk increases
- Whether safety constraints are still respected
- Whether repeat visits or NPS are negatively affected
- Whether the recommendation becomes unstable

## Recommended Actions

- Shift volume to lower-cost ASPs only where SLA and safety remain acceptable.
- Protect Climb safety gates.
- Cap allocation to cheap ASPs if quality drops at high volume.
- Flag when the budget is too low to safely cover demand.
- Recommend one or more corrective actions if infeasible:
  - Increase budget
  - Reduce scope
  - Reschedule non-critical work
  - Add temporary capacity
  - Relax non-critical constraints only with approval

---

# Scenario 2 — Demand Increase

## Demo Message

```text
How much additional field-service demand can the current ASP ecosystem absorb?
```

## KPIs to Observe

- Capacity utilization
- SLA compliance
- Budget usage
- Certified capacity coverage
- Repeat visit rate
- Safety risk index
- Feasibility status

## Expected Insight

The demo should identify the first operational bottleneck.

Possible insights:

```text
Urban may absorb additional volume more easily.
Mountain may become constrained because of travel, access and weather risk.
Climb may become constrained first because certified technicians are limited.
```

The purpose is to show that demand growth does not affect every profile equally.

## Uncertainty Management

Show demand sensitivity:

```text
Mild demand increase:      +10%
Expected demand increase:  +20%
Severe demand increase:    +40%
```

For each level, the system should show:

- Which profile becomes constrained first
- Which ASP reaches capacity first
- Whether budget is exceeded
- Whether SLA or safety risk increases
- Whether the allocation remains feasible

## Recommended Actions

- Reallocate volume to ASPs with spare capacity.
- Prioritize high-SLA ASPs for urgent or high-priority work.
- Add temporary field capacity if demand exceeds feasible limits.
- Reschedule non-critical work when demand is too high.
- Trigger procurement or vendor-development actions if capacity gaps are structural.
- Trigger training or certification actions if Climb capacity becomes the main bottleneck.

---

# Scenario 3 — Repeat Visits Become Contractually Penalized

## Demo Message

```text
What happens if repeat visits become more expensive, more visible, or contractually penalized?
```

## KPIs to Observe

- Repeat visit rate
- Average cost per task
- SLA compliance
- NPS
- Capacity usage
- Budget usage
- Customer impact / penalty risk

## Expected Insight

The demo should show that repeat visits are not only a quality KPI. They also:

- Consume additional capacity
- Increase total cost
- Damage customer experience
- Reduce NPS
- Create possible contractual penalty exposure
- Increase reputational risk, especially in high-risk or enterprise contexts

The recommendation should shift volume toward ASPs with stronger first-time-fix performance, even if they are slightly more expensive.

## Uncertainty Management

Show repeat-visit penalty sensitivity:

```text
Low penalty
Medium penalty
High penalty
```

Optionally apply profile-specific impact multipliers:

```text
Urban repeat visit impact:    Standard
Mountain repeat visit impact: Higher due to travel/access effort
Climb repeat visit impact:    Highest due to safety, reputation and complexity
```

The system should show how allocation changes as repeat visits become more important.

## Recommended Actions

- Increase the weight of repeat visits in the business scorecard.
- Allocate more work to ASPs with stronger first-time-fix performance.
- Reduce volume for ASPs with high or worsening repeat visits.
- Apply a stronger repeat-visit penalty for Climb tasks.
- Recommend root-cause analysis for ASPs with rising repeat visits.
- Use SME notes to distinguish ASP quality problems from other causes, such as:
  - Customer access issues
  - Task complexity
  - Old infrastructure
  - Reassigned or previously failed tasks

---

# Scenario 4 — Network Swap from 4G to 5G

## Demo Message

```text
How should we reallocate field-service work when the network changes from 4G to 5G and the work requires new skills, different scope, different KPIs, and more autonomous self-recovery?
```

## Why This Scenario Is Powerful

This scenario shows that prescriptive analytics is not only useful for current operations. It can also support strategic technology transformation.

The move from 4G to 5G may change:

- Required technician skills
- Required ASP certifications
- Type of field tasks
- Volume of site visits
- Complexity of incidents
- Safety requirements
- Network self-healing or self-recovery capability
- KPI priorities
- ASP suitability
- Vendor development needs

The key message:

```text
The best ASP for 4G maintenance may not be the best ASP for 5G migration or 5G operations.
```

## KPIs to Observe

### Existing KPIs

- Average cost per task
- SLA compliance
- NPS
- Repeat visit rate
- Safety risk index
- Budget usage
- Certified capacity coverage

### Additional Transformation KPIs

- 5G skill readiness
- 5G certification coverage
- First-time-right installation rate
- Site modernization success rate
- Remote-resolution ratio
- Autonomous self-recovery rate
- Manual intervention reduction
- Migration backlog
- Transformation risk index

## Expected Insight

The demo should show that the allocation model must change as network technology changes.

Expected observations:

- Some ASPs lose volume because they lack 5G skills.
- Some ASPs gain volume because they are better certified for 5G.
- Some 4G task categories shrink over time.
- Some field visits are replaced by autonomous self-recovery or remote resolution.
- Remaining field visits become more specialized and higher-value.
- ASP readiness becomes a strategic constraint, not only an operational KPI.

## Uncertainty Management

Show transformation uncertainty across rollout cases:

```text
Conservative 5G rollout:
- Lower migration speed
- More 4G support still needed
- Gradual skill transition

Expected 5G rollout:
- Balanced 4G/5G task mix
- Moderate self-recovery benefits
- Medium training gap

Accelerated 5G rollout:
- Fast migration
- High demand for 5G-certified ASPs
- Higher short-term transformation risk
```

Also show uncertainty in autonomous self-recovery:

```text
Low self-recovery:
- More field visits remain
- Higher manual intervention demand

Expected self-recovery:
- Moderate manual workload reduction
- Balanced field and remote operations

High self-recovery:
- Fewer total field visits
- Remaining visits are more specialized
- Higher skill requirements per visit
```

## Recommended Actions

- Re-score ASPs using 5G readiness criteria.
- Add 5G certification as an eligibility constraint for relevant tasks.
- Create a transition allocation plan instead of a one-time switch.
- Gradually reduce 4G-heavy ASP allocation where skills do not match future demand.
- Increase volume for ASPs with 5G skills, but cap growth to avoid operational instability.
- Use controlled pilots for ASPs newly trained in 5G work.
- Separate allocation logic for:
  - 4G legacy maintenance
  - 5G rollout/migration
  - 5G advanced operations
  - Self-recovery exception handling
- Flag skill gaps early.
- Recommend training, certification or vendor-development actions.
- Track whether higher autonomous self-recovery actually reduces field demand or only changes the type of field work required.

---

# Summary Table

| # | Scenario | Main Question | Core Value Shown |
|---:|---|---|---|
| 1 | Budget Reduction | Can we reduce cost safely? | Finds the cost-risk breaking point |
| 2 | Demand Increase | Can ASPs absorb more work? | Identifies capacity bottlenecks |
| 3 | Repeat Visits Penalized | What if poor quality becomes expensive? | Shifts focus to first-time-fix performance |
| 4 | 4G to 5G Network Swap | How does technology transformation change allocation? | Shows strategic workforce and ASP readiness planning |

---

# Recommended Positioning in the Demo

Use these four scenarios as a maturity story:

```text
Budget Reduction      → financial resilience
Demand Increase       → operational scalability
Repeat Visit Penalty  → quality and contract protection
4G to 5G Swap         → strategic transformation readiness
```

Recommended presenter message:

```text
These scenarios show that prescriptive analytics helps us test whether the recommended allocation is robust when cost, demand, quality expectations or network technology change.
```

Recommended closing message:

```text
The goal is not only to find the best allocation for today. The goal is to find an allocation strategy that remains safe, feasible and valuable under changing conditions.
```
