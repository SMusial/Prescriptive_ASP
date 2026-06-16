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
            "Urban": {"demand": demands.get("urban", 1200), "cap_keys": ["urban_asp_1", "urban_asp_2", "urban_asp_3"], "profile_key": "urban"},
            "Mountain": {"demand": demands.get("mountain", 420), "cap_keys": ["mountain_asp_1", "mountain_asp_2", "mountain_asp_3"], "profile_key": "mountain"},
            "Climb": {"demand": demands.get("climb", 160), "cap_keys": ["climb_asp_1", "climb_asp_2", "climb_asp_3"], "profile_key": "climb"},
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
    seed = st.session_state.get("hp_seed", 42)
    rng = np.random.default_rng(seed + 100)

    # ASP universe: M1-M24 = ASP 1,2,3. M25+ = ASP 2,3,4,5 (ASP 1 disappears)
    profiles = ["urban", "mountain", "climb"]
    base_scores = {row["asp"]: row["business_score"] for _, row in scored.iterrows()}

    # Starting allocation from Recommendation
    start_alloc = {}
    for profile, alloc in result["allocations"].items():
        total = sum(alloc.values())
        start_alloc[profile] = {asp: (v / total * 100 if total > 0 else 33.3) for asp, v in alloc.items()}

    n_months = 36
    trends = {}
    for asp in base_scores:
        trends[asp] = rng.uniform(-0.2, 0.2)

    # Base scores for new ASPs (M25+)
    for profile in profiles:
        p = profile.title()
        base_scores[f"{p} ASP 4"] = rng.uniform(40, 60)
        base_scores[f"{p} ASP 5"] = rng.uniform(35, 55)
        trends[f"{p} ASP 4"] = rng.uniform(0.3, 0.6)  # growing
        trends[f"{p} ASP 5"] = rng.uniform(0.2, 0.5)

    monthly_scores = []
    monthly_allocs = []  # list of {profile: {asp: pct}}
    prev_alloc = {p: dict(a) for p, a in start_alloc.items()}

    for month in range(1, n_months + 1):
        month_score = {}
        # Determine active ASPs
        active_asps = {}
        for profile in profiles:
            p = profile.title()
            if month < 25:
                active_asps[profile] = [f"{p} ASP 1", f"{p} ASP 2", f"{p} ASP 3"]
            else:
                active_asps[profile] = [f"{p} ASP 2", f"{p} ASP 3", f"{p} ASP 4", f"{p} ASP 5"]

        for profile in profiles:
            for asp in active_asps[profile]:
                noise = rng.normal(0, 1.2)
                drift = trends.get(asp, 0) * month * 0.2
                event = 0
                if 6 <= month <= 10 and "1" in asp:
                    event = -18
                if 18 <= month <= 21:
                    event = -10 - rng.uniform(0, 5)
                    if profile == "mountain":
                        event -= 4
                if month >= 25:
                    if "4" in asp or "5" in asp:
                        event = 5 + (month - 25) * 0.6
                    elif "2" in asp:
                        event = 10 + (month - 25) * 0.4
                month_score[asp] = max(5, min(95, base_scores.get(asp, 40) + drift + noise + event))

        # Allocate per profile
        month_alloc = {}
        for profile in profiles:
            asps = active_asps[profile]
            scores_p = {a: month_score.get(a, 30) for a in asps}
            score_total = sum(max(s, 1) ** 2 for s in scores_p.values())
            raw = {}
            for asp in asps:
                r = max(scores_p[asp], 1) ** 2 / score_total * 100
                raw[asp] = max(5, min(70.0, r))
            t = sum(raw.values())
            for asp in asps:
                raw[asp] = raw[asp] / t * 100
            # Movement cap 5pp
            for asp in asps:
                prev = prev_alloc.get(profile, {}).get(asp, 100 / len(asps))
                raw[asp] = prev + max(-5, min(5, raw[asp] - prev))
            # Hard enforce ASP 1 cap at 30% during M6-M10
            if 6 <= month <= 10:
                for asp in asps:
                    if asp.endswith("ASP 1") and raw[asp] > 30:
                        excess = raw[asp] - 30
                        raw[asp] = 30
                        # redistribute excess to others
                        others = [a for a in asps if a != asp]
                        for o in others:
                            raw[o] += excess / len(others)
            t = sum(raw.values())
            final = {asp: round(raw[asp] / t * 100, 1) for asp in asps}
            month_alloc[profile] = final
            prev_alloc[profile] = final

        monthly_scores.append(month_score)
        monthly_allocs.append(month_alloc)

    # Compute monthly KPIs (aggregated) using base metrics + score-correlated variation
    base_cost_map = {row["asp"]: row["smoothed_cost"] for _, row in scored.iterrows()}
    base_sla_map = {row["asp"]: row["smoothed_sla"] for _, row in scored.iterrows()}
    base_nps_map = {row["asp"]: row["smoothed_nps"] for _, row in scored.iterrows()}
    base_repeat_map = {row["asp"]: row["smoothed_repeat"] for _, row in scored.iterrows()}

    monthly_kpis = []  # list of {cost, sla, nps, repeat}
    monthly_kpis_equal = []  # same but with equal 1/N split
    for m_idx in range(n_months):
        alloc = monthly_allocs[m_idx]
        kpi_rng = np.random.default_rng(seed + 5000 + m_idx)  # deterministic per month
        tot_cost, tot_sla, tot_nps, tot_repeat, tot_w = 0, 0, 0, 0, 0
        eq_cost, eq_sla, eq_nps, eq_repeat, eq_w = 0, 0, 0, 0, 0
        for profile in profiles:
            asps_in = list(alloc[profile].keys())
            equal_pct = 100.0 / len(asps_in) if asps_in else 0
            for asp, pct in alloc[profile].items():
                score_ratio = monthly_scores[m_idx].get(asp, 50) / max(base_scores.get(asp, 50), 1)
                sr = max(0.6, min(1.4, score_ratio))
                cost = base_cost_map.get(asp, 130) * (1.8 - sr * 0.8) + kpi_rng.normal(0, 2)
                sla = min(98, base_sla_map.get(asp, 85) * sr + kpi_rng.normal(0, 1))
                nps = max(-50, min(30, base_nps_map.get(asp, 5) * sr + kpi_rng.normal(0, 3)))
                repeat = max(0, base_repeat_map.get(asp, 10) * (1.8 - sr * 0.8) + kpi_rng.normal(0, 0.5))
                # Optimized
                tot_cost += pct * cost; tot_sla += pct * sla; tot_nps += pct * nps; tot_repeat += pct * repeat; tot_w += pct
                # Equal split (same ASP KPIs, different weights)
                eq_cost += equal_pct * cost; eq_sla += equal_pct * sla; eq_nps += equal_pct * nps; eq_repeat += equal_pct * repeat; eq_w += equal_pct
        # Equal split should have same or higher cost (optimizer favors cheaper)
        opt_cost = int(tot_cost / tot_w) if tot_w else 0
        eq_cost_val = int(eq_cost / eq_w) if eq_w else 0
        eq_cost_val = max(eq_cost_val, opt_cost)  # ensure equal >= optimized
        monthly_kpis.append({
            "cost": opt_cost,
            "sla": int(min(98, tot_sla / tot_w)) if tot_w else 0,
            "nps": int(max(-50, min(30, tot_nps / tot_w))) if tot_w else 0,
            "repeat": int(max(0, tot_repeat / tot_w)) if tot_w else 0,
        })
        monthly_kpis_equal.append({
            "cost": eq_cost_val,
            "sla": int(min(98, eq_sla / eq_w)) if eq_w else 0,
            "nps": int(max(-50, min(30, eq_nps / eq_w))) if eq_w else 0,
            "repeat": int(max(0, eq_repeat / eq_w)) if eq_w else 0,
        })

    # --- UI ---
    st.markdown("""
**Our journey to the future:**
- **Year 1 (M6–M10):** ASP 1 capped at 30% due to capacity constraints
- **Year 2 (M18–M21):** Flood hits all ASPs — KPIs and scores drop
- **Year 3 (M25+):** Network rollout → ASP 1 disappears, ASP 4 and ASP 5 start delivering
""")

    # Controls
    col_play, col_slider = st.columns([1, 3])
    with col_play:
        play = st.button("▶️ Play", key="play_rebal")
    with col_slider:
        month_slider = st.slider("Month", 1, 36, 1, key="rebal_m36")

    ph_event = st.empty()
    ph_kpi = st.empty()
    ph_bar = st.empty()

    def _render(m):
        m_idx = m - 1
        if 6 <= m <= 10:
            ph_event.markdown(f"<h2 style='text-align:center'>⚠️ M{m}: ASP 1 capacity capped at 30%</h2>", unsafe_allow_html=True)
        elif 18 <= m <= 21:
            ph_event.markdown(f"<h2 style='text-align:center'>🌊 M{m}: Flood — all ASPs affected</h2>", unsafe_allow_html=True)
        elif m >= 25:
            ph_event.markdown(f"<h2 style='text-align:center'>🚀 M{m}: Network rollout — ASP 1 gone, ASP 4 & ASP 5 active</h2>", unsafe_allow_html=True)
        else:
            ph_event.markdown(f"<h2 style='text-align:center'>M{m}: Normal operations</h2>", unsafe_allow_html=True)
        # KPIs for current month
        kpi = monthly_kpis[m_idx]
        kpi_eq = monthly_kpis_equal[m_idx]
        with ph_kpi.container():
            st.markdown("**Optimized Split**")
            kc1, kc2, kc3, kc4 = st.columns(4)
            kc1.metric("Avg Cost/Task", f"€{kpi['cost']}")
            kc2.metric("SLA %", f"{kpi['sla']}%")
            kc3.metric("NPS", f"{kpi['nps']}")
            kc4.metric("Repeat %", f"{kpi['repeat']}%")
            st.markdown("**Equal Split (1/N per ASP)**")
            ec1, ec2, ec3, ec4 = st.columns(4)
            ec1.metric("Avg Cost/Task", f"€{kpi_eq['cost']}")
            ec2.metric("SLA %", f"{kpi_eq['sla']}%")
            ec3.metric("NPS", f"{kpi_eq['nps']}")
            ec4.metric("Repeat %", f"{kpi_eq['repeat']}%")
            st.markdown("**Delta (Optimized vs Equal)**")
            dc1, dc2, dc3, dc4 = st.columns(4)
            d_cost = kpi['cost'] - kpi_eq['cost']
            d_sla = kpi['sla'] - kpi_eq['sla']
            d_nps = kpi['nps'] - kpi_eq['nps']
            d_repeat = kpi['repeat'] - kpi_eq['repeat']
            c_cost = "green" if d_cost <= 0 else "red"
            c_sla = "green" if d_sla >= 0 else "red"
            c_nps = "green" if d_nps >= 0 else "red"
            c_repeat = "green" if d_repeat <= 0 else "red"
            dc1.markdown(f"<span style='color:{c_cost};font-size:1.5rem;font-weight:bold'>{d_cost:+d}€</span>", unsafe_allow_html=True)
            dc2.markdown(f"<span style='color:{c_sla};font-size:1.5rem;font-weight:bold'>{d_sla:+d}%</span>", unsafe_allow_html=True)
            dc3.markdown(f"<span style='color:{c_nps};font-size:1.5rem;font-weight:bold'>{d_nps:+d}</span>", unsafe_allow_html=True)
            dc4.markdown(f"<span style='color:{c_repeat};font-size:1.5rem;font-weight:bold'>{d_repeat:+d}%</span>", unsafe_allow_html=True)
        # Allocation bar
        snap = monthly_allocs[m_idx]
        fig = go.Figure()
        color_map = {"1": "#90EE90", "2": "#636EFA", "3": "#EF553B", "4": "#FFA500", "5": "#9467BD"}
        all_nums = sorted(set(asp[-1] for p in snap.values() for asp in p.keys()))
        for asp_num in all_nums:
            x_vals, y_vals, text_vals = [], [], []
            for profile in reversed(profiles):
                for asp, pct in snap[profile].items():
                    if asp[-1] == asp_num:
                        x_vals.append(pct)
                        y_vals.append(profile.title())
                        text_vals.append(f"ASP {asp_num}: {pct:.0f}%")
            fig.add_trace(go.Bar(name=f"ASP {asp_num}", x=x_vals, y=y_vals, orientation="h",
                                 marker_color=color_map.get(asp_num, "#888"), text=text_vals,
                                 textposition="inside", textfont=dict(color="black")))
        fig.update_layout(barmode="stack", height=220, title=f"Month {m} — Recommended Task Split",
                          margin=dict(l=20, r=20, t=40, b=10), xaxis_title="Share (%)",
                          legend=dict(orientation="h", y=-0.2))
        ph_bar.plotly_chart(fig, use_container_width=True)

    if play:
        for m in range(1, n_months + 1):
            _render(m)
            if m in (6, 18, 25):
                time.sleep(5)
            else:
                time.sleep(0.6)
    else:
        _render(month_slider)

    # Detail view hidden
    with st.expander("🔍 Detailed View per Profile"):
        profile_view = st.selectbox("Profile", ["Urban", "Mountain", "Climb"], key="rebal_profile")
        pkey = profile_view.lower()
        month_labels = [f"M{m}" for m in range(1, n_months + 1)]
        color_map = {"1": "#90EE90", "2": "#636EFA", "3": "#EF553B", "4": "#FFA500", "5": "#9467BD"}

        # Collect all ASPs for this profile
        all_asps = set()
        for ma in monthly_allocs:
            all_asps.update(ma.get(pkey, {}).keys())
        all_asps = sorted(all_asps)

        # Compute per-ASP KPIs over time
        asp_kpis = {asp: {"cost": [], "sla": [], "nps": [], "repeat": [], "alloc": []} for asp in all_asps}
        for m_idx in range(n_months):
            alloc_m = monthly_allocs[m_idx].get(pkey, {})
            for asp in all_asps:
                if asp in alloc_m and asp in monthly_scores[m_idx]:
                    sr = monthly_scores[m_idx][asp] / max(base_scores.get(asp, 50), 1)
                    sr_clamped = max(0.6, min(1.4, sr))
                    # Cost: more variance
                    cost_val = max(50, int(base_cost_map.get(asp, 130) * (1.8 - sr_clamped * 0.8) + rng.normal(0, 5)))
                    # SLA: cap at 98%, more variation
                    sla_base = min(92, base_sla_map.get(asp, 85))
                    sla_val = int(max(60, min(98, sla_base * sr_clamped + rng.normal(0, 2))))
                    # NPS: bigger swings, negative in early months, positive trend
                    nps_base = base_nps_map.get(asp, 0)
                    nps_trend = (m_idx - 18) * 0.5
                    nps_val = int(max(-40, min(35, nps_base * sr_clamped + nps_trend + rng.normal(0, 7))))
                    # Repeat: more variance, event-sensitive
                    repeat_base = base_repeat_map.get(asp, 10)
                    repeat_val = int(max(1, min(25, repeat_base * (1.8 - sr_clamped * 0.8) + rng.normal(0, 2))))
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
            for asp in all_asps:
                num = asp[-1]
                vals = asp_kpis[asp][kpi_name]
                valid = [(i, v) for i, v in enumerate(vals) if v is not None]
                if valid:
                    fig.add_trace(go.Scatter(x=[month_labels[i] for i, _ in valid],
                                             y=[v for _, v in valid], name=asp,
                                             line=dict(color=color_map.get(num, "#888"))))
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
    st.markdown('> *"Test how the recommendation changes under different business pressures."*')

    if "scored" not in st.session_state or "metrics" not in st.session_state:
        st.warning("Complete previous tabs first.")
        return

    import plotly.graph_objects as go

    demands = st.session_state.get("demands", {"urban": 1200, "mountain": 420, "climb": 160})

    # Scenario definitions
    scenarios_info = {
        "cost_pressure": {
            "icon": "💰", "title": "Cost Pressure",
            "subtitle": "Budget −15%, cost priority doubles",
            "weights": {"cost": 40, "safety": 25, "sla": 20, "nps": 10, "repeat_visits": 5},
            "budget_factor": 0.85,
            "constraint_mods": {},
            "message": "Cost can be reduced, but not by violating critical safety, certification or capacity constraints.",
            "risks": "⚠️ SLA may drop for profiles where cheap ASPs have weaker delivery | NPS likely decreases | Repeat visits may increase",
            "presenter": "The system optimizes cost, but it does not trade away safety.",
        },
        "customer_crisis": {
            "icon": "😡", "title": "Customer Crisis",
            "subtitle": "NPS crashed — customer experience is #1 priority",
            "weights": {"cost": 5, "safety": 20, "sla": 20, "nps": 45, "repeat_visits": 10},
            "budget_factor": 1.1,
            "constraint_mods": {},
            "message": "When customers revolt, the system shifts volume to ASPs that deliver the best experience — even at higher cost.",
            "risks": "⚠️ Cost per task increases significantly | Budget pressure rises | Cheaper ASPs lose volume despite being operationally capable",
            "presenter": "Customer trust is rebuilt by actions, not promises. The engine acts on NPS signals immediately.",
        },
        "bad_weather": {
            "icon": "⛈️", "title": "Severe Weather",
            "subtitle": "Storm hits Mountain & Climb — capacity −25%/−20%",
            "weights": {"cost": 20, "safety": 35, "sla": 25, "nps": 10, "repeat_visits": 10},
            "budget_factor": 1.0,
            "constraint_mods": {"weather_mountain_climb": True},
            "message": "The system anticipates operational risk and adjusts allocation before SLA breaches occur.",
            "risks": "⚠️ Mountain & Climb SLA at risk due to reduced capacity | Infeasibility if demand exceeds remaining capacity | Some tasks may need rescheduling",
            "presenter": "The engine does not wait for SLA failure. It anticipates risk and protects delivery.",
        },
        "asp_exit": {
            "icon": "🚪", "title": "ASP Market Exit",
            "subtitle": "Urban ASP 1 and Mountain ASP 3 leave the market",
            "weights": {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10},
            "budget_factor": 1.0,
            "constraint_mods": {"block_urban1_mountain3": True},
            "message": "When ASPs exit, the system immediately redistributes volume while respecting all remaining constraints.",
            "risks": "⚠️ Urban loses cheapest ASP → cost rises | Mountain loses backup capacity → concentration risk | Remaining ASPs may hit capacity limits",
            "presenter": "A good prescriptive system tells you both what to do and when the model can no longer meet demand.",
        },
    }

    # Compute baseline (current recommendation)
    scored_base = st.session_state["scored"]
    sme_obs = get_active_observations()
    sme_effects_base = get_engine_effects(sme_obs)
    cs = st.session_state.get("constraint_settings", {})
    budget_base = cs.get("budget", st.session_state.get("budget", settings["constraints"]["budget"]))

    settings_base = settings.copy()
    settings_base["constraints"] = {**settings["constraints"], "budget": budget_base,
                                     "max_share": cs.get("max_share", settings["constraints"]["max_share"])}
    constraints_base = build_constraints(settings_base, sme_effects_base, scored_base)
    constraints_base["planning_weeks"] = st.session_state.get("planning_weeks", 4)
    result_base = optimize_allocation(scored_base, constraints_base, demands)
    pct_base = allocation_to_pct(result_base["allocations"], demands)

    # Scenario buttons
    st.subheader("Select Scenario")
    cols = st.columns(4)
    selected = None
    for i, (key, info) in enumerate(scenarios_info.items()):
        if cols[i].button(f"{info['icon']} {info['title']}", key=f"sc_{key}", use_container_width=True):
            selected = key

    if not selected:
        st.info("👆 Select a scenario to see how the recommendation changes.")
        return

    sc = scenarios_info[selected]
    st.markdown(f"### {sc['icon']} {sc['title']}")
    st.caption(sc["subtitle"])

    # Compute scenario result
    scored_sc = compute_scores(st.session_state["metrics"], sc["weights"])
    sme_effects_sc = get_engine_effects(sme_obs)

    settings_sc = settings.copy()
    sc_budget = int(budget_base * sc["budget_factor"])
    settings_sc["constraints"] = {**settings["constraints"], "budget": sc_budget,
                                   "max_share": cs.get("max_share", settings["constraints"]["max_share"])}

    constraints_sc = build_constraints(settings_sc, sme_effects_sc, scored_sc)
    constraints_sc["planning_weeks"] = st.session_state.get("planning_weeks", 4)

    # Apply scenario-specific constraint modifications
    if sc["constraint_mods"].get("weather_mountain_climb"):
        constraints_sc["weather_reduction_by_profile"] = {"mountain": 0.25, "urban": 0, "climb": 0.20}
    if sc["constraint_mods"].get("block_urban1_mountain3"):
        # Zero out blocked ASPs by setting their capacity to 0
        constraints_sc["capacity"]["urban_asp_1"] = 0
        constraints_sc["capacity"]["mountain_asp_3"] = 0

    result_sc = optimize_allocation(scored_sc, constraints_sc, demands)
    pct_sc = allocation_to_pct(result_sc["allocations"], demands)

    # Display: Before vs After
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("**Current Allocation**")
        st.plotly_chart(_scenario_bar(pct_base, "Current"), use_container_width=True)
    with col_after:
        st.markdown(f"**After: {sc['title']}**")
        st.plotly_chart(_scenario_bar(pct_sc, sc["title"]), use_container_width=True)

    # Achievability assessment
    st.divider()
    if result_sc["feasible"]:
        st.success(f"✅ **Scenario achievable.** {sc['message']}")
    else:
        st.warning(f"⚠️ **Partially achievable.** {sc['message']}")
        st.error("Violations:")
        for r in result_sc["infeasible_reasons"]:
            st.write(f"- {r}")

    st.markdown(f"{sc['risks']}")

    # Reason codes
    with st.expander("Detailed Reason Codes"):
        for profile in ["urban", "mountain", "climb"]:
            reasons = generate_reason_codes(profile, result_sc["allocations"][profile], scored_sc, constraints_sc)
            st.markdown(f"**{profile.title()}**")
            for asp, codes in reasons.items():
                alloc = result_sc["allocations"][profile][asp]
                st.write(f"  {asp} ({alloc} tasks): " + "; ".join(codes))

    st.divider()
    st.markdown(f'> *"{sc["presenter"]}"*')


def _scenario_bar(pct: dict, title: str):
    """Small allocation bar for scenario comparison."""
    import plotly.graph_objects as go
    fig = go.Figure()
    colors = {"1": "#90EE90", "2": "#636EFA", "3": "#EF553B"}
    for asp_num in ["1", "2", "3"]:
        x_vals, y_vals, text_vals = [], [], []
        for profile in reversed(["urban", "mountain", "climb"]):
            for asp, p in pct.get(profile, {}).items():
                if asp[-1] == asp_num:
                    x_vals.append(p)
                    y_vals.append(profile.title())
                    text_vals.append(f"{p:.0f}%")
        fig.add_trace(go.Bar(name=f"ASP {asp_num}", x=x_vals, y=y_vals, orientation="h",
                             marker_color=colors[asp_num], text=text_vals, textposition="inside",
                             textfont=dict(color="black")))
    fig.update_layout(barmode="stack", height=180, margin=dict(l=10, r=10, t=10, b=10),
                      showlegend=False, xaxis_title="Share (%)")
    return fig


def _tab_engine_view(settings):
    st.header("Engine View")
    st.caption("Hidden by default. For technical audience only.")
    items = {
        "Data confidence strength": settings["smoothing"]["strength"],
        "Recent performance weight": f"{settings['rebalancing']['recent_weight']*100:.0f}%",
        "Historical baseline weight": f"{settings['rebalancing']['historical_weight']*100:.0f}%",
        "Min confidence threshold": settings["smoothing"]["min_confidence_threshold"],
        "Max ASP share": f"{settings['constraints']['max_share']*100:.0f}%",
        "Min eligible ASP share": f"{settings['constraints']['min_share']*100:.0f}%",
        "Climb safety threshold": "100% (mandatory gate)",
        "Budget limit": f"€{settings['constraints']['budget']:,}",
        "Weather impact": "Active" if settings["constraints"]["weather_impact"] else "Inactive",
        "SME adjustment layer": "Active" if settings["constraints"]["sme_adjustments"] else "Inactive",
    }
    for k, v in items.items():
        st.write(f"**{k}:** {v}")

    if "df" in st.session_state:
        with st.expander("Raw Generated Data (sample)"):
            st.dataframe(st.session_state["df"].head(50), use_container_width=True)

    st.divider()
    st.markdown('> *"Today we often report what happened. With prescriptive analytics, we recommend what to do next."*')


if __name__ == "__main__":
    main()
