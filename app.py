"""Dynamic ASP Allocation Optimizer — Streamlit App."""
import streamlit as st
import yaml
from pathlib import Path

from src.data_generator import generate_tasks, generate_workforce, PROFILES
from src.data_quality import assess_quality, smooth_metrics
from src.scoring import compute_scores
from src.causal_layer import compute_causal_context, compute_raw_vs_adjusted_scores, naive_vs_causal_decision, apply_sme_adjustment
from src.sme_layer import get_active_observations, get_engine_effects
from src.constraints import build_constraints
from src.optimizer import optimize_allocation, allocation_to_pct
from src.explanations import generate_reason_codes, generate_infeasibility_suggestions
from src.scenarios import apply_scenario
from src.visualization import allocation_bar_chart, sla_comparison_chart, kpi_delta_card_data, radar_chart

st.set_page_config(page_title="ASP Allocation Optimizer", layout="wide")


def load_settings() -> dict:
    p = Path(__file__).parent / "config" / "default_settings.yaml"
    with open(p) as f:
        return yaml.safe_load(f)


def main():
    st.title("Dynamic ASP Allocation Optimizer")
    st.caption("Telco Field Services — Prescriptive Analytics Demo")

    settings = load_settings()

    tabs = st.tabs(["Specification", "Setup", "Data Confidence", "Business Priorities",
                    "Causal Intelligence", "Constraints", "Recommendation",
                    "Dynamic Rebalancing", "Scenarios", "Engine View"])

    # ── TAB 0: Specification ──
    with tabs[0]:
        _tab_specification()

    # ── TAB 1: Setup ──
    with tabs[1]:
        _tab_setup(settings)

    if "df" not in st.session_state:
        st.info("Generate data in the Setup tab to begin.")
        return

    # Always compute metrics from current data (ensures downstream consistency)
    from src.data_quality import smooth_metrics as _sm
    if "metrics" not in st.session_state:
        st.session_state["metrics"] = _sm(st.session_state["df"])
    # Always ensure scored exists with default weights
    if "scored" not in st.session_state and "metrics" in st.session_state:
        _default_w = {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10}
        st.session_state["scored"] = compute_scores(st.session_state["metrics"], _default_w)

    # ── TAB 2: Data Confidence ──
    with tabs[2]:
        _tab_data_confidence()

    # ── TAB 3: Business Priorities ──
    with tabs[3]:
        _tab_priorities(settings)

    # ── TAB 4: Causal Intelligence ──
    with tabs[4]:
        _tab_causal()

    # ── TAB 5: Constraints ──
    with tabs[5]:
        _tab_constraints(settings)

    # ── TAB 6: Recommendation ──
    with tabs[6]:
        _tab_recommendation(settings)

    # ── TAB 7: Dynamic Rebalancing ──
    with tabs[7]:
        _tab_rebalancing(settings)

    # ── TAB 8: Scenarios ──
    with tabs[8]:
        _tab_scenarios(settings)

    # ── TAB 9: Engine View ──
    with tabs[9]:
        _tab_engine_view(settings)


# ────────────────────────────────────────────────────────────────
def _tab_specification():
    st.header("🎯 Dynamic ASP Allocation Optimizer")
    st.subheader("Prescriptive Analytics Demo for Telco Field Services")

    st.info('> **"How should we split field-service task volume across ASPs, considering cost, safety, SLA, NPS, repeat visits, capacity, weather, certifications, budget, data quality, and SME knowledge?"**')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👥 Target Audience")
        st.markdown("""
- Business executives & operations managers
- Product managers
- Anybody interested in contemporary analytics capabilities
""")
    with col2:
        st.markdown("#### 🔄 Today vs. Tomorrow")
        st.markdown("""
| Today | With This Demo |
|-------|---------------|
| Static rules | Dynamic optimization |
| Manual judgement | Data + SME driven |
| Limited dashboards | Prescriptive recommendations |
""")

    st.divider()

    st.markdown("#### 🏗️ Three Service Profiles")
    c1, c2, c3 = st.columns(3)
    c1.success("**🏙️ Urban**\nStandard city tasks\n\n*Challenge: Volume, cost, SLA*")
    c2.warning("**⛰️ Mountain**\nDifficult travel tasks\n\n*Challenge: Weather, access, delays*")
    c3.error("**🧗 Climb**\nRisky climbing work\n\n*Challenge: Safety, certifications*")
    st.caption("Each profile has 3 ASPs competing for task volume.")

    st.divider()

    st.markdown("#### 🧠 Five Prescriptive Capabilities")
    capabilities = [
        ("1️⃣", "Business Scorecard", "Compare ASPs across all KPIs", "#d4edda"),
        ("2️⃣", "Data Confidence Layer", "Make decisions despite imperfect data", "#cce5ff"),
        ("3️⃣", "Causal Intelligence Layer", "Understand why raw KPIs can mislead", "#fff3cd"),
        ("4️⃣", "Allocation Engine", "Get a feasible task-volume split", "#e2d9f3"),
        ("5️⃣", "Management Simulator", "Test scenarios & rebalance over time", "#f8d7da"),
    ]
    cols = st.columns(5)
    for col, (icon, name, desc, color) in zip(cols, capabilities):
        col.markdown(f"""<div style="background:{color};padding:12px;border-radius:8px;text-align:center;height:160px;color:black">
<b>{icon}<br>{name}</b><br><small>{desc}</small></div>""", unsafe_allow_html=True)

    st.divider()

    col_is, col_not = st.columns(2)
    with col_is:
        st.markdown("""#### ✅ This demo IS about
- Prescriptive analytics **capabilities** for business decisions
- How to combine data, priorities, causal context & constraints
- Demonstrating **what to do next** (not just what happened)
- Showing trade-offs, resilience & scenario planning
- Business-friendly language & visual decision support
""")
    with col_not:
        st.markdown("""#### ❌ This demo is NOT about
- A specific real-world use case or real data
- Data science implementation details or model tuning
- Production-grade ML pipeline architecture
- Real-time system integration or APIs
- Academic statistical rigor or peer-reviewed methods
""")


def _tab_setup(settings):
    st.header("Demo Setup")
    st.write("Generate a synthetic telco field-service world.")

    st.subheader("Hyperparameters")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        total_volume = st.number_input("Historical Task Volume", value=1780, min_value=200, max_value=10000, step=100, key="hp_volume")
    with c2:
        variance = st.slider("Data Variance", 0.1, 1.0, 0.5, 0.05, key="hp_variance", help="Higher = more noise/outliers")
    with c3:
        historical_weeks = st.number_input("Historical Weeks", value=4, min_value=1, max_value=52, step=1, key="hp_hist_weeks")
    with c4:
        planning_weeks = st.number_input("Planning Period (weeks)", value=4, min_value=1, max_value=12, step=1, key="hp_plan_weeks")
    with c5:
        seed = st.number_input("Random Seed", value=42, min_value=1, max_value=99999, step=1, key="hp_seed")

    # Forecast future volume: avg weekly historical × planning weeks × growth trend
    avg_weekly_volume = total_volume / max(historical_weeks, 1)
    growth_factor = 1 + 0.02 * planning_weeks  # 2% cumulative growth over planning period
    forecasted_volume = int(avg_weekly_volume * planning_weeks * growth_factor)

    st.caption(f"📈 Forecasted volume for next {planning_weeks} weeks: **{forecasted_volume:,} tasks** "
               f"({avg_weekly_volume:.0f} tasks/week × {planning_weeks} weeks × {growth_factor:.2f} growth)")

    # Distribute forecasted volume across profiles
    urban_share, mountain_share, climb_share = 0.67, 0.24, 0.09
    demands = {
        "urban": int(forecasted_volume * urban_share),
        "mountain": int(forecasted_volume * mountain_share),
        "climb": forecasted_volume - int(forecasted_volume * urban_share) - int(forecasted_volume * mountain_share),
    }
    # Historical demands for data generation
    hist_demands = {
        "urban": int(total_volume * urban_share),
        "mountain": int(total_volume * mountain_share),
        "climb": total_volume - int(total_volume * urban_share) - int(total_volume * mountain_share),
    }

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Generate Synthetic Data", type="primary"):
            df = generate_tasks(seed=int(seed), demands=hist_demands,
                                variance=variance, n_weeks=historical_weeks)
            st.session_state["df"] = df
            st.session_state["planning_weeks"] = planning_weeks
            st.session_state["demands"] = demands  # forecasted for allocation
            st.session_state["forecasted_volume"] = forecasted_volume
            # Scale budget with forecasted volume
            base_cost = 130 - (forecasted_volume / 1000) * 3
            budget = int(forecasted_volume * base_cost * (0.85 + 0.3 * variance) * 1.2)
            st.session_state["budget"] = budget
            # Scale capacity per ASP to planning weeks
            wf = generate_workforce(int(seed))
            st.session_state["workforce"] = wf
            # Clear downstream state
            for k in ["metrics", "scored", "result", "constraint_settings"]:
                st.session_state.pop(k, None)
    with col_btn2:
        if st.button("Reset Demo"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    if "df" in st.session_state:
        df = st.session_state["df"]
        fv = st.session_state.get("forecasted_volume", forecasted_volume)

        st.markdown("---")
        h_col, f_col = st.columns(2)
        with h_col:
            st.markdown("**📊 Historical Data Generated**")
            st.metric("Total Historical Tasks", f"{len(df):,}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Urban", f"{len(df[df['profile']=='urban']):,}")
            c2.metric("Mountain", f"{len(df[df['profile']=='mountain']):,}")
            c3.metric("Climb", f"{len(df[df['profile']=='climb']):,}")
        with f_col:
            st.markdown("**🔮 Forecasted Planning Period**")
            st.metric("Predicted Tasks", f"{fv:,}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Urban", f"{demands['urban']:,}")
            c2.metric("Mountain", f"{demands['mountain']:,}")
            c3.metric("Climb", f"{demands['climb']:,}")

        c4, c5, c6 = st.columns(3)
        quality = assess_quality(df)
        c4.metric("Data Quality", quality["overall_confidence"])
        c5.metric("Budget", f"€{st.session_state.get('budget', 0):,}")
        c6.metric("Weather Risk", "Moderate")

        with st.expander("📋 Sample Generated Data (all variables)"):
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)


def _tab_data_confidence():
    st.header("Data Confidence Layer")
    st.markdown('> *"We do not wait for perfect data. We make imperfect data decision-ready."*')
    df = st.session_state["df"]
    quality = assess_quality(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Missing NPS", f"{quality['missing_nps_pct']}%")
    c2.metric("Low Sample ASPs", f"{quality['low_sample_pct']}%")
    c3.metric("Outliers Detected", quality["outlier_count"])
    c4.metric("Safety Sparsity", quality["safety_sparsity"])
    c5.metric("Overall Confidence", quality["overall_confidence"])

    metrics = smooth_metrics(df)
    st.session_state["metrics"] = metrics

    import plotly.graph_objects as go

    st.subheader("Data Quality Improvements")

    # 1. Missing NPS values — handled by Bayesian smoothing
    missing_nps = int(df["nps_score"].isna().sum())
    valid_nps = int(df["nps_score"].notna().sum())
    total = len(df)

    fig_missing = go.Figure()
    fig_missing.add_trace(go.Bar(name="Valid NPS responses", x=["NPS Data"], y=[valid_nps], marker_color="#00CC96"))
    fig_missing.add_trace(go.Bar(name="Missing (smoothed via Bayesian baseline)", x=["NPS Data"], y=[missing_nps], marker_color="#EF553B"))
    fig_missing.update_layout(title=f"Missing Values: {missing_nps}/{total} NPS records missing → handled by shrinkage to profile baseline",
                              barmode="stack", height=280, yaxis_title="Task Count",
                              margin=dict(l=20, r=20, t=50, b=20))

    # 2. Outliers — winsorized before smoothing
    cost_vals = df["cost_per_task"]
    p5, p95 = cost_vals.quantile(0.05), cost_vals.quantile(0.95)
    n_outliers_low = int((cost_vals < p5).sum())
    n_outliers_high = int((cost_vals > p95).sum())
    winsorized = cost_vals.clip(p5, p95)

    fig_outliers = go.Figure()
    fig_outliers.add_trace(go.Histogram(x=cost_vals, name="Raw Cost", marker_color="#EF553B", opacity=0.6, nbinsx=40))
    fig_outliers.add_trace(go.Histogram(x=winsorized, name="After Winsorization (5th–95th)", marker_color="#00CC96", opacity=0.6, nbinsx=40))
    fig_outliers.update_layout(title=f"Outlier Handling: {n_outliers_low + n_outliers_high} extreme values clipped to 5th/95th percentile before averaging",
                               barmode="overlay", height=280, xaxis_title="Cost per Task (€)",
                               margin=dict(l=20, r=20, t=50, b=20))

    # 3. NPS before vs after Bayesian smoothing
    fig_smooth = go.Figure()
    fig_smooth.add_trace(go.Bar(name="Raw NPS (with missing/outliers)", x=metrics["asp"],
                                y=metrics["raw_nps"].fillna(0), marker_color="#EF553B"))
    fig_smooth.add_trace(go.Bar(name="Smoothed NPS (Bayesian)", x=metrics["asp"],
                                y=metrics["smoothed_nps"], marker_color="#636EFA"))
    fig_smooth.update_layout(title="Bayesian Smoothing Effect: small samples shrink toward profile baseline",
                             barmode="group", height=300, yaxis_title="NPS Score",
                             margin=dict(l=20, r=20, t=40, b=20))

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_missing, use_container_width=True)
    with col2:
        st.plotly_chart(fig_outliers, use_container_width=True)

    st.plotly_chart(fig_smooth, use_container_width=True)

    # Summary table
    st.subheader("Per-ASP Confidence After Processing")
    st.dataframe(metrics[["profile", "asp", "n_tasks", "nps_responses", "raw_nps", "smoothed_nps", "raw_cost", "smoothed_cost", "confidence"]],
                 use_container_width=True, hide_index=True)

    with st.expander("Technical Details"):
        st.markdown("""
**Method:** Empirical Bayes (Bayesian shrinkage) with winsorization.

**How it handles missing values:**
- Missing NPS responses are excluded from the observed mean calculation.
- The Bayesian formula `smoothed = (observed × n + baseline × k) / (n + k)` naturally handles this:
  fewer valid observations (`n` is small) → result is pulled strongly toward the profile baseline.
- If ALL values are missing for an ASP, the smoothed estimate equals the profile baseline entirely.
- This avoids both ignoring missing data and naively imputing zeros.

**How it handles outliers:**
- Before computing the observed mean, values are **winsorized** to the 5th–95th percentile range.
- Outliers are NOT removed — they are clipped to the boundary values (e.g., a cost of €400 in a distribution
  where P95=€220 becomes €220 for averaging purposes).
- This prevents a single extreme value from distorting the ASP's score while preserving all data points.
- After winsorization, the Bayesian smoothing provides additional stabilization.

**Confidence labels:**
- **High**: ≥30 NPS responses, >70% data completeness, ≥50 total tasks
- **Medium**: ≥10 NPS responses, >50% completeness
- **Low**: fewer than 10 responses or high missingness

**Overall confidence** is a composite: 40% missingness rate + 30% sample adequacy + 30% safety data density.

**Safety sparsity**: based on the incident rate — <2% events = "High sparsity" (hard to draw conclusions),
2–5% = "Medium", >5% = "Low sparsity" (enough events to be statistically meaningful).
""")


def _tab_priorities(settings):
    st.header("Business Priorities")
    st.markdown('> *"The definition of the best ASP changes depending on business priorities."*')

    w = settings["weights"]
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Company OKRs")
        cost_w = st.slider("Cost", 0, 100, w["cost"], key="w_cost")
        safety_w = st.slider("Safety / Security", 0, 100, w["safety"], key="w_safety")
    with col2:
        st.subheader("Contractual Goals")
        sla_w = st.slider("SLA", 0, 100, w["sla"], key="w_sla")
        nps_w = st.slider("NPS", 0, 100, w["nps"], key="w_nps")
        repeat_w = st.slider("Repeat Visits", 0, 100, w["repeat_visits"], key="w_repeat")

    weights = {"cost": cost_w, "safety": safety_w, "sla": sla_w, "nps": nps_w, "repeat_visits": repeat_w}
    total_w = sum(weights.values())
    st.markdown(f"**Total weight: {total_w}%** {'✅' if total_w == 100 else '⚠️ Must equal 100%'}")

    clicked = st.button("🔄 Update Scores & Rankings", type="primary", key="btn_update_scores")

    if clicked and total_w != 100:
        st.error("⚠️ Scoring cannot be calculated — weights must sum to exactly 100%.")
    elif clicked and "metrics" in st.session_state:
        scored = compute_scores(st.session_state["metrics"], weights)
        st.session_state["scored"] = scored
        st.session_state["weights"] = weights

    if "scored" in st.session_state:
        scored = st.session_state["scored"]
        for profile in ["urban", "mountain", "climb"]:
            st.subheader(f"{profile.title()} Profile")
            col_rank, col_radar, col_table = st.columns([1, 2, 1.5])
            pdf = scored[scored["profile"] == profile].sort_values("business_score", ascending=False)
            with col_rank:
                st.markdown("**ASP Ranking**")
                for rank, (_, row) in enumerate(pdf.iterrows(), 1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
                    st.markdown(f"{medal} **{row['asp']}** — Score: **{row['business_score']:.1f}**")
            with col_radar:
                st.plotly_chart(radar_chart(scored, profile), use_container_width=True)
            with col_table:
                st.markdown("**KPI Scores**")
                import pandas as pd
                tbl = pdf[["asp", "cost_score", "safety_score_norm", "sla_score", "nps_score_norm", "repeat_score"]].copy()
                tbl.columns = ["ASP", "Cost", "Safety", "SLA", "NPS", "Repeat"]
                tbl["ASP"] = tbl["ASP"].str.replace(f"{profile.title()} ", "")
                st.dataframe(tbl, hide_index=True, use_container_width=True)

    with st.expander("Technical Details"):
        st.markdown("""
**Method:** Multi-criteria decisioning.

**Possible production methods:** Weighted scoring, MCDA, TOPSIS, AHP, rule-based score modifiers.

**Production considerations:**
- Normalize metrics carefully
- Separate scoring logic by profile
- Treat safety for Climb as a hard constraint
- Store priority templates (Cost Mode, SLA Mode, Safety Mode)
""")


def _tab_causal():
    st.header("Causal Intelligence Layer")
    st.markdown('> *"Do we know who performs better — or just who received easier work?"*')
    df = st.session_state["df"]
    weights = st.session_state.get("weights", {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10})
    ctx = compute_causal_context(df)
    scored = st.session_state.get("scored")
    ctx_scored = compute_raw_vs_adjusted_scores(ctx, weights, scored)
    observations = get_active_observations()

    # STEP 1: Data-based causal adjustment on overall score
    st.subheader("Step 1: Overall Score Adjusted for Task Difficulty")
    st.markdown("Raw overall score vs causally-adjusted score (accounting for complexity and emergency share):")

    import plotly.graph_objects as go
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(name="Raw Overall Score", x=ctx_scored["asp"], y=ctx_scored["raw_score"], marker_color="#EF553B"))
    fig1.add_trace(go.Bar(name="Adjusted (Data)", x=ctx_scored["asp"], y=ctx_scored["adjusted_score_data"], marker_color="#636EFA"))
    fig1.update_layout(barmode="group", height=300, margin=dict(l=20, r=20, t=30, b=20),
                       yaxis_title="Overall Business Score (0-100)")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("**Task Difficulty Context (from data)**")
    st.dataframe(ctx_scored[["asp", "complexity_ratio", "travel_ratio", "weather_ratio", "access_ratio", "causal_adjustment"]],
                 hide_index=True, use_container_width=True)

    hardest = ctx_scored.loc[ctx_scored["avg_complexity"].idxmax()]
    st.info(f"🔍 **Key Finding:** {hardest['asp']} handles the most complex tasks "
            f"(complexity {hardest['complexity_ratio']:.2f}×, travel {hardest['travel_ratio']:.2f}×, "
            f"weather {hardest['weather_ratio']:.2f}×, access {hardest['access_ratio']:.2f}×) — "
            f"raw score {hardest['raw_score']:.1f} → adjusted to {hardest['adjusted_score_data']:.1f} (+{hardest['causal_adjustment']:.1f} pts).")

    st.divider()

    # STEP 2: SME observations + final adjustment
    st.subheader("Step 2: SME Observations")
    for obs in observations:
        if obs["profile"] == "mountain":
            st.warning(f"**{obs['source_role']}:** {obs['business_observation']}")

    ctx_final = apply_sme_adjustment(ctx_scored, observations)

    # Update scored dataframe: apply causal + SME adjustments as deltas to Mountain ASPs
    if "scored" in st.session_state:
        scored_updated = st.session_state["scored"].copy()
        for _, row in ctx_final.iterrows():
            mask = scored_updated["asp"] == row["asp"]
            total_adjustment = row["causal_adjustment"] + row["sme_adjustment"]
            current = scored_updated.loc[mask, "business_score"].values[0]
            scored_updated.loc[mask, "business_score"] = max(0, min(100, current + total_adjustment))
        st.session_state["scored"] = scored_updated

    st.subheader("Overall Score: Raw → Data-Adjusted → Data+SME")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Raw Score", x=ctx_final["asp"], y=ctx_final["raw_score"], marker_color="#EF553B"))
    fig2.add_trace(go.Bar(name="Adjusted (Data)", x=ctx_final["asp"], y=ctx_final["adjusted_score_data"], marker_color="#636EFA"))
    fig2.add_trace(go.Bar(name="Final (Data + SME)", x=ctx_final["asp"], y=ctx_final["final_score"], marker_color="#00CC96"))
    fig2.update_layout(barmode="group", height=300, margin=dict(l=20, r=20, t=30, b=20),
                       yaxis_title="Overall Business Score (0-100)")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Conclusions & Recommendations
    st.subheader("Conclusions & Recommendations")
    decision = naive_vs_causal_decision(ctx_final)

    col1, col2 = st.columns(2)
    with col1:
        st.error(f"**❌ Naive decision (raw data only):**\n\n{decision['naive_decision']}")
    with col2:
        st.success(f"**✅ Informed decision (data + causal + SME):**\n\n{decision['causal_decision']}")

    raw_ranking = ctx_final.sort_values("raw_score", ascending=False)["asp"].tolist()
    adj_ranking = ctx_final.sort_values("final_score", ascending=False)["asp"].tolist()
    best_final = ctx_final.loc[ctx_final["final_score"].idxmax()]
    hardest_asp = ctx_final.loc[ctx_final["avg_complexity"].idxmax()]

    summary_points = [
        f"- **{hardest_asp['asp']}** receives hardest tasks (complexity: {hardest_asp['avg_complexity']:.2f}, emergency: {hardest_asp['emergency_share']:.0f}%)",
        f"- Raw score ranking: {' > '.join(raw_ranking)}",
        f"- Final ranking (data+SME): {' > '.join(adj_ranking)}",
        f"- {'Rankings changed!' if decision['ranking_changed'] else 'Rankings stable, but gaps shifted significantly'}",
        f"- **Recommendation:** {best_final['asp']} is effectively strongest (final score: {best_final['final_score']:.1f}). Protect ASPs handling harder work from unfair volume cuts.",
    ]
    st.markdown("\n".join(summary_points))

    with st.expander("Technical Details"):
        st.markdown("""
**Method:** Causal inference and expert-informed causal reasoning.

**Possible production methods:** Causal graphs, counterfactual analysis, propensity score adjustment, treatment effect estimation, difference-in-differences, causal forests.

**Production considerations:**
- Capture treatment/assignment policy variables
- Track task complexity and assignment bias
- Store SME observations as structured assumptions with expiry and confidence
""")


def _tab_constraints(settings):
    st.header("Operational Constraints")
    st.markdown('> *"The engine does not simply choose the best ASP. It chooses the best feasible allocation."*')

    c = settings["constraints"]
    demands = st.session_state.get("demands", {"urban": 1200, "mountain": 420, "climb": 160})
    planning_weeks = st.session_state.get("planning_weeks", 4)

    # Toggles
    cap_on = st.toggle("ASP Capacity Limits", value=True, key="cap_on")
    weather_on = st.toggle("Weather / Security Risk", value=c["weather_impact"], key="weather_on")
    cert_on = st.toggle("Skills & Certifications", value=True, key="cert_on")
    budget_val = st.number_input("Field Activity Budget (€)", value=st.session_state.get("budget", c["budget"]), step=5000, key="budget_val")
    max_rework = st.slider("Max Acceptable Rework Rate (%)", 5, 30, 15, 1, key="max_rework", help="ASPs above this rate get penalized")
    max_share = st.slider("Max ASP Share per Profile", 0.30, 0.80, c["max_share"], 0.05, key="max_share_val")

    # Weather prediction based on planning period
    if weather_on:
        weather_forecast = _generate_weather_forecast(planning_weeks, st.session_state.get("hp_seed", 42))
    else:
        weather_forecast = {"urban": 0, "mountain": 0, "climb": 0}

    # Workforce model
    if cert_on:
        workforce = generate_workforce(st.session_state.get("hp_seed", 42))
    else:
        workforce = {}

    apply_clicked = st.button("✅ Apply Constraints", type="primary", key="btn_apply_constraints")

    if apply_clicked:
        st.session_state["constraint_settings"] = {
            "capacity_on": cap_on, "weather_on": weather_on, "cert_on": cert_on,
            "budget": budget_val, "max_rework": max_rework, "max_share": max_share,
            "weather_forecast": weather_forecast, "workforce": workforce,
        }
        st.success("Constraints applied.")

    # Show active constraints after applying
    if "constraint_settings" in st.session_state:
        st.divider()
        st.subheader("Active Constraints per Profile")

        cs = st.session_state["constraint_settings"]
        wf = cs.get("weather_forecast", weather_forecast)
        cap_cfg = settings.get("capacity", {})
        profiles_display = {
            "Urban": {"demand": demands.get("urban", 1200), "cap_keys": ["cityconnect", "urbanlink", "streetnet"], "profile_key": "urban"},
            "Mountain": {"demand": demands.get("mountain", 420), "cap_keys": ["alpinereach", "summitfield", "alpingmbh"], "profile_key": "mountain"},
            "Climb": {"demand": demands.get("climb", 160), "cap_keys": ["skyclimb", "towerpro", "verticalworks"], "profile_key": "climb"},
        }

        weather_reasons = {
            "urban": "flood risk",
            "mountain": "snow & thunderstorms",
            "climb": "wind, thunderstorm, ice, high-pressure chimney risk",
        }

        cols = st.columns(3)
        for col, (profile, info) in zip(cols, profiles_display.items()):
            with col:
                st.markdown(f"**{profile}** ({info['demand']} tasks)")
                lines = []
                if cs["capacity_on"]:
                    caps = ", ".join([f"{cap_cfg.get(k, '∞')}" for k in info["cap_keys"]])
                    lines.append(f"📦 Capacity: {caps} tasks/ASP")
                reduction = wf.get(info["profile_key"], 0)
                if cs["weather_on"] and reduction > 0:
                    lines.append(f"🌧️ Weather: −{int(reduction*100)}% capacity ({weather_reasons[info['profile_key']]})")
                if cs["cert_on"] and profile == "Climb":
                    lines.append("🎓 Uncertified ASPs → 0 tasks")
                if cs["cert_on"] and cs.get("workforce"):
                    asps = [a for a in cs["workforce"] if a.startswith(profile)]
                    for asp in sorted(asps):
                        w = cs["workforce"][asp]
                        lines.append(f"👷 {asp.split(' ')[-1]}: {w['senior']}% Sr / {w['regular']}% Reg / {w['junior']}% Jr")
                lines.append(f"💰 Budget: €{int(cs['budget'] * info['demand'] / sum(demands.values())):,}")
                lines.append(f"📊 Max share: {int(cs['max_share']*100)}%")
                lines.append(f"🔄 Rework cap: {cs['max_rework']}%")
                for t in lines:
                    st.write(t)

        # Show weather forecast detail
        if cs["weather_on"]:
            with st.expander(f"🌤️ Weather Forecast ({planning_weeks}-week outlook)"):
                for pkey, reasons in weather_reasons.items():
                    red = wf.get(pkey, 0)
                    if red > 0:
                        st.write(f"**{pkey.title()}:** {int(red*100)}% capacity loss — {reasons}")
                    else:
                        st.write(f"**{pkey.title()}:** No significant impact expected")

    with st.expander("Technical Details"):
        st.markdown("""
**Method:** Constrained optimization.

**Possible production methods:** Linear programming, mixed-integer programming, goal programming, robust optimization, constraint programming.

**Production considerations:**
- Separate hard constraints from soft preferences
- Safety and certification = hard constraints for Climb
- Weather prediction simulates capacity loss per profile based on seasonal/weekly forecast
- Rework rate limit penalizes ASPs with excessive repeat visits
- Explain infeasibility clearly
- Keep full audit trail
""")


def _generate_weather_forecast(planning_weeks: int, seed: int) -> dict:
    """Simulate weather forecast for the planning period. Returns capacity reduction per profile."""
    import numpy as np
    rng = np.random.default_rng(seed + planning_weeks)
    # Longer planning = more chance of bad weather
    base_risk = min(0.5, planning_weeks * 0.06)
    return {
        "urban": round(rng.uniform(0, base_risk * 0.4), 2),       # floods: rare
        "mountain": round(rng.uniform(base_risk * 0.3, base_risk), 2),  # snow/storms: moderate
        "climb": round(rng.uniform(base_risk * 0.5, base_risk * 1.3), 2),  # wind/ice/storms: highest
    }


def _compute_weighted_kpis(scored_df, allocations, demands):
    """Compute weighted-average KPIs given an allocation."""
    total_cost, total_sla, total_nps, total_repeat, total_tasks = 0, 0, 0, 0, 0
    for profile, alloc in allocations.items():
        for asp, tasks in alloc.items():
            if tasks == 0:
                continue
            row = scored_df[scored_df["asp"] == asp]
            if row.empty:
                continue
            r = row.iloc[0]
            total_cost += tasks * r["smoothed_cost"]
            total_sla += tasks * r["smoothed_sla"]
            total_nps += tasks * r["smoothed_nps"]
            total_repeat += tasks * r["smoothed_repeat"]
            total_tasks += tasks
    if total_tasks == 0:
        return {"Avg Cost/Task": 0, "SLA %": 0, "NPS": 0, "Repeat %": 0}
    return {
        "Avg Cost/Task": total_cost / total_tasks,
        "SLA %": total_sla / total_tasks,
        "NPS": total_nps / total_tasks,
        "Repeat %": total_repeat / total_tasks,
    }


def _tab_recommendation(settings):
    planning_weeks = st.session_state.get("planning_weeks", 4)
    st.header(f"Recommended Allocation — Next {planning_weeks} Weeks")

    if "scored" not in st.session_state:
        st.warning("Set Business Priorities first.")
        return

    scored = st.session_state["scored"]
    cs = st.session_state.get("constraint_settings", {})
    demands = st.session_state.get("demands", {"urban": 1200, "mountain": 420, "climb": 160})

    # Build constraints from ALL inputs
    budget = cs.get("budget", st.session_state.get("budget", settings["constraints"]["budget"]))
    max_share = cs.get("max_share", settings["constraints"]["max_share"])
    weather_on = cs.get("weather_on", True)
    weather_forecast = cs.get("weather_forecast", {"urban": 0, "mountain": 0, "climb": 0})

    sme_obs = get_active_observations()
    sme_effects = get_engine_effects(sme_obs)

    # Build full constraints with actual UI values
    settings_mod = settings.copy()
    settings_mod["constraints"] = {**settings["constraints"],
                                    "budget": budget,
                                    "max_share": max_share,
                                    "climb_safety_threshold": 90,
                                    "weather_impact": weather_on}
    full_constraints = build_constraints(settings_mod, sme_effects, scored)
    full_constraints["planning_weeks"] = planning_weeks

    # Apply weather forecast from constraints page
    if weather_on:
        full_constraints["weather_reduction_by_profile"] = weather_forecast

    result = optimize_allocation(scored, full_constraints, demands)
    st.session_state["result"] = result
    pct = allocation_to_pct(result["allocations"], demands)

    # ── Decision Journey Summary ──
    st.markdown("---")
    st.subheader("📋 Decision Journey: From Problem to Recommendation")
    j1, j2, j3, j4 = st.columns(4)
    j1.markdown("""<div style="background:#e8f4fd;padding:10px;border-radius:8px;text-align:center;color:black">
<b>1. Data</b><br><small>Generated & cleaned<br>Bayesian smoothing</small></div>""", unsafe_allow_html=True)
    j2.markdown("""<div style="background:#fff3cd;padding:10px;border-radius:8px;text-align:center;color:black">
<b>2. Priorities</b><br><small>Weighted scoring<br>Business OKRs + KPIs</small></div>""", unsafe_allow_html=True)
    j3.markdown("""<div style="background:#e2d9f3;padding:10px;border-radius:8px;text-align:center;color:black">
<b>3. Context</b><br><small>Causal adjustment<br>SME knowledge</small></div>""", unsafe_allow_html=True)
    j4.markdown("""<div style="background:#d4edda;padding:10px;border-radius:8px;text-align:center;color:black">
<b>4. Optimize</b><br><small>Constraints applied<br>Feasible split</small></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Feasibility Status ──
    if not result["feasible"]:
        st.warning("⚠️ Partial infeasibility — showing best achievable allocation.")
        for r in result["infeasible_reasons"]:
            st.write(f"- {r}")
    else:
        st.success("✅ Feasible allocation found within all constraints.")

    # ── Overall Chart ──
    st.subheader("Recommended Task Split (All Profiles)")
    st.plotly_chart(allocation_bar_chart(pct, result["allocations"]), use_container_width=True)

    # Overall KPI impact aggregated across all profiles
    st.subheader("Expected KPI Impact (vs equal 1/3 split)")
    kpi_labels = ["Avg Cost/Task", "SLA %", "NPS", "Repeat %"]
    equal_alloc_all = {}
    for profile in ["urban", "mountain", "climb"]:
        profile_asps = list(result["allocations"][profile].keys())
        d = demands.get(profile, 0)
        equal_alloc_all[profile] = {asp: d // len(profile_asps) for asp in profile_asps}
    rec_kpis = _compute_weighted_kpis(scored, result["allocations"], demands)
    eq_kpis = _compute_weighted_kpis(scored, equal_alloc_all, demands)
    kpi_cols = st.columns(4)
    for col, label in zip(kpi_cols, kpi_labels):
        delta = rec_kpis[label] - eq_kpis[label]
        dc = "inverse" if label in ["Avg Cost/Task", "Repeat %"] else "normal"
        col.metric(label, f"{rec_kpis[label]:.1f}", f"{delta:+.1f} vs equal", delta_color=dc)

    st.metric("Total Estimated Cost", f"€{result['total_cost']:,.0f}", f"Budget: €{budget:,}")

    # ── Profile Detail (hidden by default) ──
    st.markdown("---")
    with st.expander("🔍 Detailed View per Profile"):
        selected_profile = st.selectbox("Select Profile", ["Urban", "Mountain", "Climb"], key="rec_profile")
        profile_key = selected_profile.lower()
        profile_alloc = result["allocations"][profile_key]
        profile_pct = pct[profile_key]
        profile_demand = demands.get(profile_key, 0)

        st.markdown(f"**{selected_profile} — Demand: {profile_demand:,} tasks**")
        r_cols = st.columns(3)
        reasons = generate_reason_codes(profile_key, profile_alloc, scored, full_constraints)
        for i, (asp, codes) in enumerate(reasons.items()):
            alloc = profile_alloc[asp]
            share = profile_pct[asp]
            bg = "#d4edda" if share >= 40 else "#fff3cd" if share >= 20 else "#f8d7da"
            with r_cols[i % 3]:
                asp_score = scored[scored["asp"] == asp]["business_score"].values
                score_str = f"Score: {asp_score[0]:.1f}" if len(asp_score) > 0 else ""
                st.markdown(f"""<div style="background:{bg};padding:12px;border-radius:8px;color:black;margin-bottom:8px">
<b>{asp}</b><br>📊 {alloc} tasks ({share:.0f}%)<br>🏆 {score_str}<br><small>{'<br>'.join(codes)}</small></div>""", unsafe_allow_html=True)

        st.markdown(f"**Expected KPI Impact for {selected_profile} (vs equal 1/3 split)**")
        profile_asps = list(profile_alloc.keys())
        per_asp_equal = profile_demand // len(profile_asps)
        equal_profile = {asp: per_asp_equal for asp in profile_asps}
        rec_profile_kpis = _compute_weighted_kpis(scored, {profile_key: profile_alloc}, {profile_key: profile_demand})
        eq_profile_kpis = _compute_weighted_kpis(scored, {profile_key: equal_profile}, {profile_key: profile_demand})
        kpi_cols = st.columns(4)
        for col, label in zip(kpi_cols, kpi_labels):
            rec_val = rec_profile_kpis[label]
            delta = rec_val - eq_profile_kpis[label]
            dc = "inverse" if label in ["Avg Cost/Task", "Repeat %"] else "normal"
            col.metric(label, f"{rec_val:.1f}", f"{delta:+.1f} vs equal", delta_color=dc)

        with st.expander(f"Constraints active for {selected_profile}"):
            st.write(f"- Max share per ASP: {int(max_share*100)}% = {int(profile_demand * max_share)} tasks")
            st.write(f"- Planning weeks factor: {planning_weeks}/4 = {planning_weeks/4:.2f}×")
            wr = weather_forecast.get(profile_key, 0)
            if wr > 0:
                st.write(f"- Weather capacity reduction: −{int(wr*100)}%")
            sme_caps = full_constraints.get("asp_max_share", {})
            for asp, cap in sme_caps.items():
                if profile_key in asp.lower():
                    st.write(f"- SME cap: {asp} ≤ {int(cap*100)}%")
            if profile_key == "climb":
                inelig = full_constraints.get("climb_ineligible", [])
                if inelig:
                    st.write(f"- Ineligible (certification): {', '.join(inelig)}")
                else:
                    st.write("- All Climb ASPs certified ✓")

    # ── Final Message ──
    st.markdown("---")
    st.markdown('> *"Prescriptive analytics is not just one algorithm. It combines business priorities, imperfect data, '
                'SME knowledge, causal reasoning, and constraints to recommend what the company should do next."*')


def _run_rebalancing_sim(scored, result, demands, seed, max_share_pct):
    """Run the 36-month simulation deterministically. Returns cached dict."""
    import numpy as np
    profiles = ["urban", "mountain", "climb"]
    base_scores = {row["asp"]: row["business_score"] for _, row in scored.iterrows()}
    base_cost_map = {row["asp"]: row["smoothed_cost"] for _, row in scored.iterrows()}
    base_sla_map = {row["asp"]: row["smoothed_sla"] for _, row in scored.iterrows()}
    base_nps_map = {row["asp"]: row["smoothed_nps"] for _, row in scored.iterrows()}
    base_repeat_map = {row["asp"]: row["smoothed_repeat"] for _, row in scored.iterrows()}

    start_alloc = {}
    for profile, alloc in result["allocations"].items():
        total = sum(alloc.values())
        start_alloc[profile] = {asp: (v / total * 100 if total > 0 else 33.3) for asp, v in alloc.items()}

    n_months = 36
    sim_rng = np.random.default_rng(seed + 200)
    trends = {asp: sim_rng.uniform(-0.2, 0.2) for asp in base_scores}
    for profile in profiles:
        p = profile.title()
        base_scores[f"{p} ASP 4"] = sim_rng.uniform(40, 60)
        base_scores[f"{p} ASP 5"] = sim_rng.uniform(35, 55)
        trends[f"{p} ASP 4"] = sim_rng.uniform(0.3, 0.6)
        trends[f"{p} ASP 5"] = sim_rng.uniform(0.2, 0.5)

    # ASP name mappings for rebalancing
    asp_names = {"urban": ["CityConnect", "UrbanLink", "StreetNet"],
                 "mountain": ["AlpineReach", "SummitField", "AlpinGmbH"],
                 "climb": ["SkyClimb", "TowerPro", "VerticalWorks"]}
    asp_new = {"urban": ["UrbanLink", "StreetNet", "Urban ASP 4", "Urban ASP 5"],
               "mountain": ["SummitField", "AlpinGmbH", "Mountain ASP 4", "Mountain ASP 5"],
               "climb": ["TowerPro", "VerticalWorks", "Climb ASP 4", "Climb ASP 5"]}
    monthly_scores = []
    monthly_allocs = []
    prev_alloc = {p: dict(a) for p, a in start_alloc.items()}    # First ASP per profile (the one that gets capped/removed)
    asp_first = {"urban": "CityConnect", "mountain": "AlpineReach", "climb": "SkyClimb"}
    asp_second = {"urban": "UrbanLink", "mountain": "SummitField", "climb": "TowerPro"}

    for month in range(1, n_months + 1):
        m_rng = np.random.default_rng(seed + 300 + month)
        month_score = {}
        active_asps = {}
        for profile in profiles:
            p = profile.title()
            if month < 25:
                active_asps[profile] = asp_names[profile]
            else:
                active_asps[profile] = asp_new[profile]
        for profile in profiles:
            for asp in active_asps[profile]:
                noise = m_rng.normal(0, 1.2)
                drift = trends.get(asp, 0) * month * 0.2
                event = 0
                if 6 <= month <= 10 and asp == asp_first[profile]:
                    event = -18
                if 18 <= month <= 21:
                    event = -10 - m_rng.uniform(0, 5)
                    if profile == "mountain":
                        event -= 4
                if month >= 25:
                    if asp.startswith("Urban ASP") or asp.startswith("Mountain ASP") or asp.startswith("Climb ASP"):
                        event = 5 + (month - 25) * 0.6  # new ASPs growing
                    elif asp == asp_second[profile]:
                        event = 10 + (month - 25) * 0.4
                month_score[asp] = max(5, min(95, base_scores.get(asp, 40) + drift + noise + event))

        if month == 1:
            monthly_scores.append(month_score)
            monthly_allocs.append({p: dict(a) for p, a in start_alloc.items()})
            continue

        month_alloc = {}
        for profile in profiles:
            asps = active_asps[profile]
            scores_p = {a: month_score.get(a, 30) for a in asps}
            score_total = sum(max(s, 1) ** 2 for s in scores_p.values())
            raw = {asp: max(5, min(max_share_pct, max(scores_p[asp], 1) ** 2 / score_total * 100)) for asp in asps}
            t = sum(raw.values())
            raw = {a: raw[a] / t * 100 for a in asps}
            for asp in asps:
                prev = prev_alloc.get(profile, {}).get(asp, 100 / len(asps))
                raw[asp] = prev + max(-5, min(5, raw[asp] - prev))
            if 6 <= month <= 10:
                for asp in asps:
                    if asp == asp_first[profile] and raw[asp] > 30:
                        excess = raw[asp] - 30
                        raw[asp] = 30
                        for o in [a for a in asps if a != asp]:
                            raw[o] += excess / (len(asps) - 1)
            for asp in asps:
                if raw[asp] > max_share_pct:
                    excess = raw[asp] - max_share_pct
                    raw[asp] = max_share_pct
                    for o in [a for a in asps if a != asp]:
                        raw[o] += excess / (len(asps) - 1)
            t = sum(raw.values())
            month_alloc[profile] = {asp: round(raw[asp] / t * 100, 1) for asp in asps}
            prev_alloc[profile] = month_alloc[profile]
        monthly_scores.append(month_score)
        monthly_allocs.append(month_alloc)

    # KPIs
    weights_used = st.session_state.get("weights", {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10})
    w_total = sum(weights_used.values()) or 100
    w_factor = {"cost": weights_used.get("cost", 20) / w_total, "sla": weights_used.get("sla", 25) / w_total,
                "nps": weights_used.get("nps", 15) / w_total, "repeat": weights_used.get("repeat_visits", 10) / w_total}

    rec_kpis_m1 = _compute_weighted_kpis(scored, result["allocations"], demands)
    equal_alloc_m1 = {p: {a: sum(result["allocations"][p].values()) // len(result["allocations"][p])
                          for a in result["allocations"][p]} for p in profiles}
    eq_kpis_m1 = _compute_weighted_kpis(scored, equal_alloc_m1, demands)

    monthly_kpis, monthly_kpis_equal = [], []
    for m_idx in range(n_months):
        if m_idx == 0:
            monthly_kpis.append({"cost": int(rec_kpis_m1["Avg Cost/Task"]), "sla": int(rec_kpis_m1["SLA %"]),
                                 "nps": int(rec_kpis_m1["NPS"]), "repeat": int(rec_kpis_m1["Repeat %"])})
            monthly_kpis_equal.append({"cost": int(eq_kpis_m1["Avg Cost/Task"]), "sla": int(eq_kpis_m1["SLA %"]),
                                       "nps": int(eq_kpis_m1["NPS"]), "repeat": int(eq_kpis_m1["Repeat %"])})
            continue
        alloc = monthly_allocs[m_idx]
        kpi_rng = np.random.default_rng(seed + 5000 + m_idx)
        tot_cost, tot_sla, tot_nps, tot_repeat, tot_w = 0, 0, 0, 0, 0
        eq_cost, eq_sla, eq_nps, eq_repeat, eq_w = 0, 0, 0, 0, 0

        # M18-M21: flood crisis — SLA/NPS collapse for non-mountain, cost rises
        month = m_idx + 1
        in_crisis = 18 <= month <= 21

        for profile in profiles:
            asps_in = list(alloc[profile].keys())
            equal_pct = 100.0 / len(asps_in) if asps_in else 0
            for asp, pct in alloc[profile].items():
                sr = max(0.6, min(1.4, monthly_scores[m_idx].get(asp, 50) / max(base_scores.get(asp, 50), 1)))
                # Base KPI values
                cost = base_cost_map.get(asp, 130) * (1.8 - sr * 0.8) + kpi_rng.normal(0, 4)
                sla = min(98, base_sla_map.get(asp, 85) * sr + kpi_rng.normal(0, 3))
                # NPS: starts negative, trends positive toward +35 over 36 months
                nps_trend = -25 + (m_idx / 36) * 60  # from -25 to +35
                nps = nps_trend + kpi_rng.normal(0, 5)
                repeat = max(0, base_repeat_map.get(asp, 10) * (1.8 - sr * 0.8) + kpi_rng.normal(0, 1.5))

                # Crisis impact M18-M21: Urban & Climb hit
                if in_crisis and profile != "mountain":
                    intensity = min(1.0, (month - 17) / 2)
                    if month > 19:
                        intensity *= (21 - month) / 2
                    cost += 15 * intensity
                    sla -= 12 * intensity
                    nps -= 30 * intensity  # severe NPS collapse during flood
                    repeat += 4 * intensity

                # Clamp
                cost = max(50, cost)
                sla = max(55, min(98, sla))
                nps = max(-60, min(40, nps))
                repeat = max(1, min(25, repeat))

                tot_cost += pct * cost; tot_sla += pct * sla; tot_nps += pct * nps; tot_repeat += pct * repeat; tot_w += pct
                eq_cost += equal_pct * cost; eq_sla += equal_pct * sla; eq_nps += equal_pct * nps; eq_repeat += equal_pct * repeat; eq_w += equal_pct
        opt_cost = int(tot_cost / tot_w) if tot_w else 0
        opt_sla = int(min(98, tot_sla / tot_w)) if tot_w else 0
        opt_nps = int(max(-50, min(30, tot_nps / tot_w))) if tot_w else 0
        opt_repeat = int(max(0, tot_repeat / tot_w)) if tot_w else 0
        eq_cost_v = int(eq_cost / eq_w) if eq_w else 0
        eq_sla_v = int(min(98, eq_sla / eq_w)) if eq_w else 0
        eq_nps_v = int(max(-50, min(30, eq_nps / eq_w))) if eq_w else 0
        eq_repeat_v = int(max(0, eq_repeat / eq_w)) if eq_w else 0
        # Weight-driven: higher weight = better optimization, weight < 10% = risk of negative impact
        boost = 10
        cost_risk = -3 if w_factor["cost"] < 0.10 else 0
        sla_risk = -4 if w_factor["sla"] < 0.10 else 0
        nps_risk = -8 if w_factor["nps"] < 0.10 else 0
        repeat_risk = 2 if w_factor["repeat"] < 0.10 else 0
        opt_cost = int(opt_cost - boost * w_factor["cost"] * 2 + cost_risk)
        opt_sla = int(min(98, opt_sla + boost * w_factor["sla"] * 2 + sla_risk))
        opt_nps = int(max(-60, min(40, opt_nps + boost * w_factor["nps"] * 8 + nps_risk)))
        opt_repeat = int(max(0, opt_repeat - boost * w_factor["repeat"] + repeat_risk))
        # Equal split NPS should be worse (no optimization benefit)
        eq_nps_v = int(eq_nps_v - 5)
        eq_cost_v = max(eq_cost_v, opt_cost)
        monthly_kpis.append({"cost": opt_cost, "sla": opt_sla, "nps": opt_nps, "repeat": opt_repeat})
        monthly_kpis_equal.append({"cost": eq_cost_v, "sla": eq_sla_v, "nps": eq_nps_v, "repeat": eq_repeat_v})

    return {"allocs": monthly_allocs, "scores": monthly_scores, "kpis": monthly_kpis,
            "kpis_equal": monthly_kpis_equal, "n_months": n_months, "base_scores": base_scores,
            "base_cost_map": base_cost_map, "base_sla_map": base_sla_map,
            "base_nps_map": base_nps_map, "base_repeat_map": base_repeat_map}


def _tab_rebalancing(settings):
    st.header("Dynamic Rebalancing")
    st.markdown('> *"Prescriptive analytics is not a one-time recommendation. It is an adaptive decision capability."*')

    if "result" not in st.session_state or "scored" not in st.session_state:
        st.warning("Complete the Recommendation tab first.")
        return

    import numpy as np
    import plotly.graph_objects as go
    import time

    scored = st.session_state["scored"]
    result = st.session_state["result"]
    demands = st.session_state.get("demands", {"urban": 1200, "mountain": 420, "climb": 160})
    seed = st.session_state.get("hp_seed", 42)
    cs = st.session_state.get("constraint_settings", {})
    max_share_pct = cs.get("max_share", 0.60) * 100

    # Cache simulation so it's identical across reruns (invalidates when recommendation changes)
    result_hash = int(result.get("total_cost", 0))
    cache_key = f"rebal_cache_{seed}_{max_share_pct}_{result_hash}"
    # Clear old caches
    old_keys = [k for k in st.session_state if k.startswith("rebal_cache_") and k != cache_key]
    for k in old_keys:
        del st.session_state[k]
    if cache_key not in st.session_state:
        _sim = _run_rebalancing_sim(scored, result, demands, seed, max_share_pct)
        st.session_state[cache_key] = _sim
    sim = st.session_state[cache_key]
    monthly_allocs = sim["allocs"]
    monthly_scores = sim["scores"]
    monthly_kpis = sim["kpis"]
    monthly_kpis_equal = sim["kpis_equal"]
    n_months = sim["n_months"]
    base_scores = sim["base_scores"]
    base_cost_map = sim["base_cost_map"]
    base_sla_map = sim["base_sla_map"]
    base_nps_map = sim["base_nps_map"]
    base_repeat_map = sim["base_repeat_map"]
    profiles = ["urban", "mountain", "climb"]
    # --- UI ---
    # Controls
    total_tasks_pm = sum(int(v) for v in demands.values())
    ph_journey = st.empty()
    ph_journey.markdown("""
**Our journey to the future:**
- **Year 1 (M6–M10):** CityConnect/AlpineReach/SkyClimb capped at 30% due to capacity constraints
- **Year 2 (M18–M21):** Flood hits Urban & Climb — SLA and NPS collapse, significant cost increase. Mountain not affected.
- **Year 3 (M25+):** Network rollout → First ASP exits, new ASPs start delivering
""")

    col_play, col_reset = st.columns([1, 1])
    with col_play:
        play = st.button("▶️ Play", key="play_rebal")
    with col_reset:
        reset = st.button("⏮️ Reset", key="reset_rebal")
    month_slider = st.slider("Month", 1, 36, 1, key="rebal_m36")

    # ASP name maps for color consistency
    asp_names = {"urban": ["CityConnect", "UrbanLink", "StreetNet"],
                 "mountain": ["AlpineReach", "SummitField", "AlpinGmbH"],
                 "climb": ["SkyClimb", "TowerPro", "VerticalWorks"]}
    asp_new = {"urban": ["UrbanLink", "StreetNet", "Urban ASP 4", "Urban ASP 5"],
               "mountain": ["SummitField", "AlpinGmbH", "Mountain ASP 4", "Mountain ASP 5"],
               "climb": ["TowerPro", "VerticalWorks", "Climb ASP 4", "Climb ASP 5"]}

    ph_event = st.empty()
    ph_bar = st.empty()
    ph_kpi = st.empty()

    def _render(m):
        m_idx = m - 1
        if 6 <= m <= 10:
            color, text = "#fff3cd", f"\u26a0\ufe0f M{m}: First ASP capacity capped at 30%"
        elif 18 <= m <= 21:
            color, text = "#cce5ff", f"\U0001f30a M{m}: Flood \u2014 Urban & Climb hit (SLA/NPS collapse, cost +15\u20ac). Mountain OK."
        elif m >= 25:
            color, text = "#ffffff", f"\U0001f680 M{m}: Network rollout \u2014 First ASP gone, new ASPs active"
        else:
            color, text = "#d4edda", f"M{m}: Normal operations"
        ph_event.markdown(f'<div style="background:{color};padding:16px;border-radius:8px;text-align:center"><span style="font-size:1.5rem;font-weight:bold;color:black">{text}</span></div>', unsafe_allow_html=True)
        # Allocation bar first
        snap = monthly_allocs[m_idx]
        fig = go.Figure()
        # Fixed color per ASP name: first ASP=green (gone M25+), 2nd=blue, 3rd=red, new=orange/purple
        asp_color_map = {}
        for p in profiles:
            names = asp_names[p]
            asp_color_map[names[0]] = "#90EE90"  # green (exits M25)
            asp_color_map[names[1]] = "#636EFA"  # blue (stays)
            asp_color_map[names[2]] = "#EF553B"  # red (stays)
        for p in profiles:
            new = asp_new[p]
            for i, a in enumerate(new):
                if a not in asp_color_map:
                    asp_color_map[a] = "#FFA500" if i >= 2 and "4" in a else "#9467BD"
        for profile in reversed(profiles):
            asps_list = list(snap[profile].keys())
            for asp in asps_list:
                pct = snap[profile][asp]
                fig.add_trace(go.Bar(name=asp, x=[pct], y=[profile.title()], orientation="h",
                                     marker_color=asp_color_map.get(asp, "#888"),
                                     text=[f"{asp}: {pct:.0f}%"], textposition="inside",
                                     textfont=dict(color="black"), showlegend=(profile == "urban")))
        fig.update_layout(barmode="stack", height=220, title=f"Month {m} \u2014 Recommended Task Split",
                          margin=dict(l=20, r=20, t=40, b=10), xaxis_title="Share (%)",
                          legend=dict(orientation="h", y=-0.2))
        ph_bar.plotly_chart(fig, use_container_width=True)
        # KPIs
        kpi = monthly_kpis[m_idx]
        kpi_eq = monthly_kpis_equal[m_idx]
        # Moving averages of delta (optimized - equal) for last 3 months
        w_start = max(0, m_idx - 2)
        w_len = m_idx - w_start + 1
        ma_sla = sum(monthly_kpis[i]["sla"] - monthly_kpis_equal[i]["sla"] for i in range(w_start, m_idx + 1)) // w_len
        ma_nps = sum(monthly_kpis[i]["nps"] - monthly_kpis_equal[i]["nps"] for i in range(w_start, m_idx + 1)) // w_len
        ma_repeat = sum(monthly_kpis[i]["repeat"] - monthly_kpis_equal[i]["repeat"] for i in range(w_start, m_idx + 1)) // w_len
        cum_savings = sum((monthly_kpis_equal[i]["cost"] - monthly_kpis[i]["cost"]) * total_tasks_pm for i in range(m_idx + 1))
        with ph_kpi.container():
            st.markdown("**Optimized Split**")
            kc1, kc2, kc3, kc4 = st.columns(4)
            kc1.metric("Avg Cost/Task", f"\u20ac{kpi['cost']}")
            kc2.metric("SLA %", f"{kpi['sla']}%")
            kc3.metric("NPS", f"{kpi['nps']}")
            kc4.metric("Repeat %", f"{kpi['repeat']}%")
            st.markdown("**Equal Split (1/N per ASP)**")
            ec1, ec2, ec3, ec4 = st.columns(4)
            ec1.metric("Avg Cost/Task", f"\u20ac{kpi_eq['cost']}")
            ec2.metric("SLA %", f"{kpi_eq['sla']}%")
            ec3.metric("NPS", f"{kpi_eq['nps']}")
            ec4.metric("Repeat %", f"{kpi_eq['repeat']}%")
            st.markdown("**Delta**")
            dc1, dc2, dc3, dc4 = st.columns(4)
            sav_color = "green" if cum_savings >= 0 else "red"
            c_sla = "green" if ma_sla >= 0 else "red"
            c_nps = "green" if ma_nps >= 0 else "red"
            c_repeat = "green" if ma_repeat <= 0 else "red"
            dc1.markdown(f"<span style='color:{sav_color};font-size:1.5rem;font-weight:bold'>\u20ac{cum_savings:,}</span><br><small>Cumulated savings</small>", unsafe_allow_html=True)
            dc2.markdown(f"<span style='color:{c_sla};font-size:1.5rem;font-weight:bold'>{ma_sla:+d}%</span><br><small>MA \u0394 SLA</small>", unsafe_allow_html=True)
            dc3.markdown(f"<span style='color:{c_nps};font-size:1.5rem;font-weight:bold'>{ma_nps:+d}</span><br><small>MA \u0394 NPS</small>", unsafe_allow_html=True)
            dc4.markdown(f"<span style='color:{c_repeat};font-size:1.5rem;font-weight:bold'>{ma_repeat:+d}%</span><br><small>MA \u0394 Repeat</small>", unsafe_allow_html=True)

    if play:
        ph_journey.empty()  # hide journey text during animation
        for m in range(1, n_months + 1):
            _render(m)
            if m in (6, 18, 25):
                time.sleep(5)
            else:
                time.sleep(0.6)
    elif reset:
        # Hide everything on reset
        ph_event.empty()
        ph_bar.empty()
        ph_kpi.empty()
    else:
        _render(month_slider)

    # Detail view hidden
    with st.expander("🔍 Detailed View per Profile"):
        profile_view = st.selectbox("Profile", ["Urban", "Mountain", "Climb"], key="rebal_profile")
        pkey = profile_view.lower()
        month_labels = [f"M{m}" for m in range(1, n_months + 1)]
        colors_list = ["#90EE90", "#636EFA", "#EF553B", "#FFA500", "#9467BD"]

        # Collect all ASPs for this profile
        all_asps = set()
        for ma in monthly_allocs:
            all_asps.update(ma.get(pkey, {}).keys())
        all_asps = sorted(all_asps)

        # Compute per-ASP KPIs over time
        asp_kpis = {asp: {"cost": [], "sla": [], "nps": [], "repeat": [], "alloc": []} for asp in all_asps}
        for m_idx in range(n_months):
            alloc_m = monthly_allocs[m_idx].get(pkey, {})
            det_rng = np.random.default_rng(seed + 7000 + m_idx)
            for asp in all_asps:
                if asp in alloc_m and asp in monthly_scores[m_idx]:
                    sr = monthly_scores[m_idx][asp] / max(base_scores.get(asp, 50), 1)
                    sr_clamped = max(0.6, min(1.4, sr))
                    cost_val = max(50, int(base_cost_map.get(asp, 130) * (1.8 - sr_clamped * 0.8) + det_rng.normal(0, 5)))
                    sla_base = min(92, base_sla_map.get(asp, 85))
                    sla_val = int(max(60, min(98, sla_base * sr_clamped + det_rng.normal(0, 2))))
                    nps_base = base_nps_map.get(asp, 0)
                    nps_trend = (m_idx - 18) * 0.5
                    nps_val = int(max(-40, min(35, nps_base * sr_clamped + nps_trend + det_rng.normal(0, 7))))
                    repeat_base = base_repeat_map.get(asp, 10)
                    repeat_val = int(max(1, min(25, repeat_base * (1.8 - sr_clamped * 0.8) + det_rng.normal(0, 2))))
                    asp_kpis[asp]["cost"].append(cost_val)
                    asp_kpis[asp]["sla"].append(sla_val)
                    asp_kpis[asp]["nps"].append(nps_val)
                    asp_kpis[asp]["repeat"].append(repeat_val)
                    asp_kpis[asp]["alloc"].append(alloc_m[asp])
                else:
                    for k in ["cost", "sla", "nps", "repeat", "alloc"]:
                        asp_kpis[asp][k].append(None)

        # Plot each KPI
        for kpi_name, title, yrange in [
            ("cost", "Cost per Task (€)", [40, 250]),
            ("sla", "SLA %", [55, 105]),
            ("nps", "NPS", [-45, 40]),
            ("repeat", "Repeat %", [0, 28]),
            ("alloc", "Allocation Share %", [0, 75]),
        ]:
            fig = go.Figure()
            for idx, asp in enumerate(all_asps):
                vals = asp_kpis[asp][kpi_name]
                valid = [(i, v) for i, v in enumerate(vals) if v is not None]
                if valid:
                    fig.add_trace(go.Scatter(x=[month_labels[i] for i, _ in valid],
                                             y=[v for _, v in valid], name=asp,
                                             line=dict(color=colors_list[idx % len(colors_list)])))
            layout = {"height": 250, "title": title, "margin": dict(l=20, r=20, t=40, b=20)}
            if yrange:
                layout["yaxis_range"] = yrange
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("Technical Details"):
        st.markdown("""
**Method:** Adaptive monthly rebalancing.

- Starts from Recommendation output, evolves 36 months
- Max 70% to any ASP (30% during capacity events)
- 5pp/month movement cap prevents overreaction
- Year 3: ASP universe changes (ASP 1 exits, ASP 4 & 5 enter)

**Production:** Rolling optimization, Bayesian updating, contextual bandits.
""")


def _tab_scenarios(settings):
    st.header("What-If Scenarios")
    st.markdown('> *"How resilient is our allocation when cost, demand, quality or technology change?"*')

    if "scored" not in st.session_state or "metrics" not in st.session_state:
        st.warning("Complete previous tabs first.")
        return

    import plotly.graph_objects as go

    demands = st.session_state.get("demands", {"urban": 1200, "mountain": 420, "climb": 160})
    scored_base = st.session_state["scored"]
    cs = st.session_state.get("constraint_settings", {})
    budget_base = cs.get("budget", st.session_state.get("budget", settings["constraints"]["budget"]))

    # Baseline allocation
    sme_obs = get_active_observations()
    sme_effects = get_engine_effects(sme_obs)
    settings_base = settings.copy()
    settings_base["constraints"] = {**settings["constraints"], "budget": budget_base,
                                     "max_share": cs.get("max_share", settings["constraints"]["max_share"])}
    constraints_base = build_constraints(settings_base, sme_effects, scored_base)
    constraints_base["planning_weeks"] = st.session_state.get("planning_weeks", 4)
    result_base = optimize_allocation(scored_base, constraints_base, demands)
    pct_base = allocation_to_pct(result_base["allocations"], demands)

    # Scenario definitions (3 scenarios, no repeat penalty)
    scenarios = {
        "budget": {"icon": "💰", "title": "Budget Reduction", "subtitle": "Can we reduce cost without breaking performance?",
                   "levels": [("Mild −5%", 0.95), ("Expected −15%", 0.85), ("Severe −25%", 0.75)]},
        "demand": {"icon": "📈", "title": "Demand Increase", "subtitle": "How much more can our ASP ecosystem absorb?",
                   "levels": [("Mild +10%", 1.10), ("Expected +20%", 1.20), ("Severe +40%", 1.40)]},
        "5g": {"icon": "📡", "title": "4G → 5G Network Swap", "subtitle": "How does technology transformation change allocation?",
               "levels": [("Conservative rollout", 0.2), ("Expected rollout", 0.5), ("Accelerated rollout", 0.8)]},
    }

    # Scenario selector
    cols = st.columns(3)
    selected = None
    for i, (key, sc) in enumerate(scenarios.items()):
        if cols[i].button(f"{sc['icon']} {sc['title']}", key=f"sc_{key}", use_container_width=True):
            selected = key

    if not selected:
        st.info("👆 Select a scenario to explore allocation resilience.")
        st.markdown("""
| Scenario | Core Question | Value |
|---|---|---|
| 💰 Budget Reduction | Can we reduce cost safely? | Finds cost-risk breaking point |
| 📈 Demand Increase | Can ASPs absorb more work? | Identifies capacity bottlenecks |
| 📡 4G → 5G Swap | How does transformation change allocation? | Strategic readiness planning |
""")
        return

    sc = scenarios[selected]
    st.markdown(f"### {sc['icon']} {sc['title']}")
    st.caption(sc["subtitle"])

    # Run scenario at each uncertainty level
    results_levels = []
    for label, factor in sc["levels"]:
        scored_sc = compute_scores(st.session_state["metrics"],
                                   st.session_state.get("weights", {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10}))
        settings_sc = settings.copy()
        demands_sc = dict(demands)
        constraints_sc_settings = {**settings["constraints"], "max_share": cs.get("max_share", settings["constraints"]["max_share"])}

        if selected == "budget":
            constraints_sc_settings["budget"] = int(budget_base * factor)
            cost_w = 20 + int((1 - factor) * 200)
            w_budget = {"cost": cost_w, "safety": 20, "sla": 15, "nps": 10, "repeat_visits": 5}
            scored_sc = compute_scores(st.session_state["metrics"], w_budget)
            # Also increase smoothed_cost for expensive ASPs to amplify difference
            scored_sc.loc[scored_sc["business_score"] < 40, "smoothed_cost"] *= (1 + (1 - factor))
        elif selected == "demand":
            demands_sc = {p: int(v * factor) for p, v in demands.items()}
            # Higher demand = tighter capacity = lower SLA for overloaded ASPs
            scored_sc.loc[scored_sc["business_score"] < 50, "smoothed_sla"] *= (2 - factor)
        elif selected == "5g":
            # Penalize legacy ASPs heavily
            for asp in ["CityConnect", "AlpineReach", "SkyClimb"]:
                scored_sc.loc[scored_sc["asp"] == asp, "business_score"] *= max(0.05, 1 - factor * 0.9)
            # Increase cost significantly for 5G swap work
            cost_multiplier = 1 + factor * 0.6  # conservative=+12%, expected=+30%, accelerated=+48%
            scored_sc["smoothed_cost"] = scored_sc["smoothed_cost"] * cost_multiplier
            # Accelerated rollout: add 2 new 5G-specialist ASPs per profile
            if factor >= 0.8:
                import pandas as pd
                new_asps = []
                for profile in ["urban", "mountain", "climb"]:
                    prof_data = scored_sc[scored_sc["profile"] == profile].iloc[0].to_dict()
                    for suffix, score_boost in [("5G-Alpha", 1.3), ("5G-Beta", 1.15)]:
                        new = dict(prof_data)
                        new["asp"] = f"{profile.title()} {suffix}"
                        new["business_score"] = prof_data["business_score"] * score_boost
                        new["smoothed_cost"] = prof_data["smoothed_cost"] * 1.2  # 5G specialists cost more
                        new_asps.append(new)
                scored_sc = pd.concat([scored_sc, pd.DataFrame(new_asps)], ignore_index=True)
            constraints_sc_settings["budget"] = int(budget_base * (1 + factor * 0.5))

        settings_sc["constraints"] = constraints_sc_settings
        c_sc = build_constraints(settings_sc, sme_effects, scored_sc)
        c_sc["planning_weeks"] = st.session_state.get("planning_weeks", 4)
        r_sc = optimize_allocation(scored_sc, c_sc, demands_sc)
        pct_sc = allocation_to_pct(r_sc["allocations"], demands_sc)
        results_levels.append({"label": label, "result": r_sc, "pct": pct_sc, "demands": demands_sc})

    # Display: Baseline + 2 what-if levels (3 columns total)
    st.subheader("Task Split: Baseline → What-If")
    level_cols = st.columns(3)
    # Baseline first
    with level_cols[0]:
        st.markdown("**📋 Baseline (current)**")
        st.plotly_chart(_scenario_bar(pct_base, "Baseline"), use_container_width=True, key=f"sc_bar_{selected}_base")
        st.metric("Cost", f"€{result_base['total_cost']:,.0f}")
    # Two what-if levels (mild and severe)
    for i, idx in enumerate([0, 2]):  # show mild and severe
        rl = results_levels[idx]
        with level_cols[i + 1]:
            feasible_icon = "✅" if rl["result"]["feasible"] else "⚠️"
            st.markdown(f"**{rl['label']}** {feasible_icon}")
            st.plotly_chart(_scenario_bar(rl["pct"], rl["label"]), use_container_width=True, key=f"sc_bar_{selected}_{i}")
            st.metric("Cost", f"€{rl['result']['total_cost']:,.0f}")
            if not rl["result"]["feasible"]:
                for r in rl["result"]["infeasible_reasons"]:
                    st.caption(f"❌ {r}")

    # Resilience score (realistic: typically 40-75 range)
    st.subheader("Resilience Assessment")
    feasible_count = sum(1 for rl in results_levels if rl["result"]["feasible"])
    base_kpis = _compute_weighted_kpis(scored_base, result_base["allocations"], demands)
    kpi_penalty = 0
    for rl in results_levels:
        k = _compute_weighted_kpis(scored_base, rl["result"]["allocations"], rl["demands"])
        if abs(k["SLA %"] - base_kpis["SLA %"]) > 3:
            kpi_penalty += 8
        if abs(k["NPS"] - base_kpis["NPS"]) > 5:
            kpi_penalty += 6
        if abs(k["Avg Cost/Task"] - base_kpis["Avg Cost/Task"]) > 10:
            kpi_penalty += 5
    resilience = max(15, min(85, int(feasible_count * 25 + 30 - kpi_penalty)))
    res_color = "#00CC96" if resilience >= 65 else "#FFA500" if resilience >= 40 else "#EF553B"

    st.markdown(f"""
<div style="padding:12px;border-radius:8px;border:2px solid {res_color};display:inline-block">
<span style="font-size:1.1rem;font-weight:bold">Resilience Score: </span>
<span style="font-size:1.8rem;font-weight:bold;color:{res_color}">{resilience}/100</span>
<span style="font-size:0.9rem;margin-left:12px">— How robust is the allocation? (100 is unachievable — uncertainty always exists)</span>
</div>
""", unsafe_allow_html=True)

    # Traffic light trade-off squares
    st.markdown("")
    zone_cols = st.columns(3)
    zone_labels = ["🟢 Safe Zone", "🟡 Watch Zone", "🔴 Risk Zone"]
    zone_colors = ["#d4edda", "#fff3cd", "#f8d7da"]
    for i, (col, rl) in enumerate(zip(zone_cols, results_levels)):
        kpis = _compute_weighted_kpis(scored_base, rl["result"]["allocations"], rl["demands"])
        sla_d = kpis["SLA %"] - base_kpis["SLA %"]
        nps_d = kpis["NPS"] - base_kpis["NPS"]
        cost_d = kpis["Avg Cost/Task"] - base_kpis["Avg Cost/Task"]
        feasible = rl["result"]["feasible"]
        with col:
            st.markdown(f"""<div style="background:{zone_colors[i]};padding:14px;border-radius:8px;color:black;min-height:200px">
<b>{zone_labels[i]}</b><br><b>{rl['label']}</b><br><br>
{"✅ Feasible" if feasible else "❌ Infeasible"}<br>
Cost: {cost_d:+.0f}\u20ac/task<br>
SLA: {sla_d:+.1f}%<br>
NPS: {nps_d:+.1f}<br>
Total: \u20ac{rl['result']['total_cost']:,.0f}
</div>""", unsafe_allow_html=True)

    # Recommended actions with specific figures
    st.subheader("Recommended Actions")
    mild_cost = results_levels[0]["result"]["total_cost"]
    severe_cost = results_levels[2]["result"]["total_cost"]
    base_cost = result_base["total_cost"]

    if selected == "budget":
        actions = [
            ("🟢", sc["levels"][0][0], f"Approve — saves \u20ac{base_cost - mild_cost:,.0f}, shift {int(abs(pct_base['urban'].get('CityConnect',0) - results_levels[0]['pct']['urban'].get('CityConnect',0)))}pp to CityConnect"),
            ("🟡", sc["levels"][1][0], f"Discuss — saves \u20ac{base_cost - results_levels[1]['result']['total_cost']:,.0f} but SLA may drop {abs(_compute_weighted_kpis(scored_base, results_levels[1]['result']['allocations'], demands)['SLA %'] - base_kpis['SLA %']):.1f}%"),
            ("🔴", sc["levels"][2][0], f"Escalate — \u20ac{severe_cost:,.0f} total, reduce scope by ~{int(sum(demands.values())*0.1)} tasks or add \u20ac{int((base_cost-severe_cost)*0.3):,} budget"),
        ]
    elif selected == "demand":
        extra_tasks = int(sum(demands.values()) * 0.4)
        actions = [
            ("🟢", sc["levels"][0][0], f"Approve — {int(sum(demands.values())*0.1):,} extra tasks absorbed within capacity"),
            ("🟡", sc["levels"][1][0], f"Plan — {int(sum(demands.values())*0.2):,} extra tasks, monitor Climb capacity (closest to limit)"),
            ("🔴", sc["levels"][2][0], f"Act — {extra_tasks:,} extra tasks, add ≥2 temporary crews or defer {int(extra_tasks*0.3):,} non-critical tasks"),
        ]
    elif selected == "5g":
        actions = [
            ("🟢", sc["levels"][0][0], f"Prepare — re-score 9 ASPs on 5G readiness, identify 3 ASPs needing training within 6 months"),
            ("🟡", sc["levels"][1][0], f"Transition — onboard 2 new 5G-specialist ASPs, increase cost budget by ~\u20ac{int(severe_cost*0.15):,} for swap sites"),
            ("🔴", sc["levels"][2][0], f"Transform — 500+ swap sites/month, add ASP 4 & ASP 5, cost +40%, separate 4G legacy from 5G ops"),
        ]
    for icon, level, action in actions:
        st.markdown(f"{icon} **{level}:** {action}")

    # Closing
    st.divider()
    st.markdown('> *"The goal is not only the best allocation for today — it\'s an allocation strategy that remains safe, feasible and valuable under changing conditions."*')


def _scenario_bar(pct: dict, title: str):
    """Small allocation bar for scenario comparison."""
    import plotly.graph_objects as go
    fig = go.Figure()
    colors_list = ["#90EE90", "#636EFA", "#EF553B"]
    for profile in reversed(["urban", "mountain", "climb"]):
        asps = list(pct.get(profile, {}).keys())
        for idx, asp in enumerate(asps):
            p = pct[profile][asp]
            fig.add_trace(go.Bar(name=asp, x=[p], y=[profile.title()], orientation="h",
                                 marker_color=colors_list[idx % len(colors_list)],
                                 text=[f"{p:.0f}%"], textposition="inside",
                                 textfont=dict(color="black"), showlegend=(profile == "urban")))
    fig.update_layout(barmode="stack", height=180, margin=dict(l=10, r=10, t=10, b=10),
                      showlegend=False, xaxis_title="Share (%)")
    return fig


def _tab_engine_view(settings):
    st.header("Engine View")
    st.caption("Technical reference for analytics teams.")

    st.markdown("""
<table style="width:100%;border-collapse:collapse;font-size:0.95rem">
<tr>
<th style="padding:10px;text-align:center;width:40px">#</th>
<th style="padding:10px">Capability</th>
<th style="padding:10px;color:#5dade2">Method in This Demo</th>
<th style="padding:10px;color:#af7ac5">Production-Grade Methods</th>
</tr>
<tr>
<td style="padding:8px;text-align:center;font-size:2.5rem">📊</td>
<td style="padding:8px"><b>Business Scorecard</b></td>
<td style="padding:8px;color:#85c1e9">Weighted scoring (0–100), global normalization, score² allocation</td>
<td style="padding:8px;color:#d2b4de">Multi-Criteria Decision Analysis (MCDA), Technique for Order of Preference by Similarity (TOPSIS), Analytic Hierarchy Process (AHP), Bayesian decision networks</td>
</tr>
<tr>
<td style="padding:8px;text-align:center;font-size:2.5rem">🧹</td>
<td style="padding:8px"><b>Data Confidence</b></td>
<td style="padding:8px;color:#85c1e9">Empirical Bayes shrinkage + winsorization (P5/P95)</td>
<td style="padding:8px;color:#d2b4de">Hierarchical Bayesian models, Gaussian Processes (GP), Multiple Imputation by Chained Equations (MICE)</td>
</tr>
<tr>
<td style="padding:8px;text-align:center;font-size:2.5rem">🧠</td>
<td style="padding:8px"><b>Causal Intelligence</b></td>
<td style="padding:8px;color:#85c1e9">Task difficulty ratios + SME knowledge deltas</td>
<td style="padding:8px;color:#d2b4de">Directed Acyclic Graphs (DAG), Propensity Score Matching (PSM), Causal Forests, Difference-in-Differences (DiD)</td>
</tr>
<tr>
<td style="padding:8px;text-align:center;font-size:2.5rem">🎯</td>
<td style="padding:8px"><b>Allocation Engine</b></td>
<td style="padding:8px;color:#85c1e9">Score²-proportional + winner bonus + constraint clipping</td>
<td style="padding:8px;color:#d2b4de">Linear Programming (LP), Mixed-Integer Programming (MIP), Robust Optimization (RO)</td>
</tr>
<tr>
<td style="padding:8px;text-align:center;font-size:2.5rem">⏱️</td>
<td style="padding:8px"><b>Dynamic Rebalancing</b></td>
<td style="padding:8px;color:#85c1e9">Monthly score simulation + 5pp movement cap</td>
<td style="padding:8px;color:#d2b4de">Contextual Bandits (CB), Reinforcement Learning (RL), Rolling Horizon Optimization (RHO)</td>
</tr>
<tr>
<td style="padding:8px;text-align:center;font-size:2.5rem">🧪</td>
<td style="padding:8px"><b>Scenario Simulation</b></td>
<td style="padding:8px;color:#85c1e9">Priority/constraint override + re-optimization</td>
<td style="padding:8px;color:#d2b4de">Monte Carlo Simulation (MCS), Stochastic Programming (SP), Digital Twins (DT)</td>
</tr>
</table>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown('> *"Today we often report what happened. With prescriptive analytics, we recommend what to do next."*')


if __name__ == "__main__":
    main()
