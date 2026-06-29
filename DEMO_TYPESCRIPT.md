# Demo Typescript — 45 Minutes
## Dynamic Allocation Optimizer | Prescriptive Analytics

**Role:** Decision Intelligence Lead
**Audience:** Mixed (business executives, operations, product managers, analytics)
**Style:** Short, confident, results-focused. Let the demo speak. Minimal words, maximum impact.

---

## Tab 1: Demo Scope (2 min)

> "Today I'll show you what prescriptive analytics actually looks like in practice.
> Not theory. Not a dashboard. A working decision engine."

*Click → show audience & context*

> "This is relevant for anyone making allocation decisions under uncertainty — regardless of your role."

*Click → show DI process flow*

> "Nine capabilities. We'll demonstrate six of them live today."

*Click → show IS / IS NOT*

> "Important: this is about capabilities, not a specific production system."

---

## Tab 2: Use Case (2 min)

> "Our use case: 9 field-service partners across 3 profiles. Today they each get 33%. Equal split. No intelligence."

*Click → show profiles*

> "Urban is volume. Mountain is access difficulty. Climb is safety-critical. Very different challenges."

*Click → show baseline*

> "This is where we start. The question is: can we do better?"

---

## Tab 3: Setup (1 min)

> "I'll generate synthetic data. 1,780 tasks, 4 weeks of history. The system forecasts demand for the planning period."

*Click Generate*

> "Historical data on the left. Forecasted demand on the right. Budget scales automatically."

---

## Tab 4: Data Confidence (3 min)

> "Real operational data is never perfect. We have missing NPS values, outliers, sparse safety events."

*Click → show improvements*

> "Bayesian smoothing. We don't wait for perfect data — we make imperfect data decision-ready.
> Small samples get pulled toward the baseline. Outliers get clipped, not removed."

---

## Tab 5: Business Priorities (3 min)

> "Now the key question: what does this company optimise for? Cost? Safety? SLA? NPS?"

*Set weights to 20/30/25/15/10 (default). Click Update.*

> "Watch how the ranking changes. The 'best ASP' depends entirely on what you prioritise.
> Look at Mountain — SummitField wins on cost and safety. AlpineReach wins on quality."

*Optional: shift to Cost=60, rest lower. Click Update.*

> "See? CityConnect jumps to first. The cheapest always wins when cost is king — but look at the SLA trade-off."

*Reset to default before moving on.*

---

## Tab 6: Causal Intelligence (5 min)

> "Now the most important insight. Raw scores can be misleading."

*Show raw score chart*

> "AlpineReach looks weak. But let's ask: why?"

*Click → show data adjustment*

> "Because they handle the hardest tasks. Higher complexity, longer travel, more emergencies.
> When we adjust for difficulty, the picture changes."

*Click → show SME observations*

> "SME knowledge adds what data alone cannot see. The dispatcher knows about emergency expertise. The operations manager knows about quality at high volume."

*Click → show conclusions*

> "Naive decision: reduce AlpineReach. Informed decision: keep them for hard work, but cap at 45%.
> This is why causal intelligence matters."

---

## Tab 7: Constraints (2 min)

> "The engine doesn't just pick the best ASP. It finds the best feasible allocation."

*Toggle constraints, set values. Click Apply.*

> "Capacity limits. Weather forecast. Skills requirements. Budget. Max share. Rework caps.
> Every constraint is visible and adjustable."

---

## Tab 8: Recommendation (4 min)

> "Now the prescriptive answer."

*Click Generate Recommended Task Split*

> "Not a ranking. Not a dashboard. A concrete task allocation with reason codes."

*Click Show Expected KPI Impact*

> "Compared to equal split: lower cost, better SLA, improved NPS. That's the value of prescriptive analytics."

---

## Tab 9: Dynamic Rebalancing (8 min)

> "But allocation is not a one-time decision. It must adapt."

*Click Start Simulation*

> "36 months. Three major events. Watch how the system responds."

*Click Play*

> "Month 6: UrbanLink gets capped — internal capacity issue. The system redistributes immediately."

*[Pause at M6 — 5 seconds]*

> "Month 18: Flood hits Urban and Climb. Cost spikes. NPS collapses. Mountain is unaffected."

*[Pause at M18 — 5 seconds]*

> "Month 25: Network rollout. First ASP exits. New ASPs enter. The model adapts to a completely new landscape."

*[Pause at M25 — 5 seconds]*

> "Look at the delta row. Cumulated savings. Moving average of KPIs. This is continuous optimisation."

---

## Tab 10: Scenarios (6 min)

> "What if conditions change? Let's test resilience."

*Click Budget Reduction*

> "Budget drops 25%. CityConnect goes from 10% to 47% — cheapest wins. But Climb stays protected.
> Resilience score: 72. Not perfect, but manageable."

*Click 4G → 5G Swap*

> "Accelerated rollout. First ASPs disappear. New 5G-specialist ASPs enter. Cost increases 48%.
> But resilience is 92 — the model handles transformation well."

> "The system doesn't just optimise for today. It tells you how robust your plan is under stress."

---

## Tab 11: Engine View (2 min)

> "For the technical audience: here's what's under the hood."

*Point to the table*

> "Simple methods for the demo. Production requires the full portfolio — LP, causal forests, reinforcement learning, digital twins. Calibrated to scale and criticality."

---

## Tab 12: Closing (2 min)

*Let the screen speak. Pause.*

> "Today we report what happened. With prescriptive analytics, we recommend what to do next. Adaptive. Explainable. Continuous."

*Pause 3 seconds*

> "Thank you. Questions?"

---

## Notes

- **Total: ~40 min content + 5 min buffer for questions during demo**
- **Default seed: 42** — gives good causal flip for Mountain
- **Always click buttons in order** — data flows left to right
- **If asked about production timeline:** "6-9 months for first capability, 18 months for full DI platform"
- **If asked about data requirements:** "We start with what you have. The confidence layer handles imperfection."
- **If asked about cost:** "The demo itself proves the value — look at the KPI delta. That's your business case."
