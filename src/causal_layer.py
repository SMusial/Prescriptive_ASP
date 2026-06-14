"""Causal intelligence layer — reveals why raw KPIs can mislead."""
import pandas as pd
import numpy as np


def compute_causal_context(df: pd.DataFrame) -> pd.DataFrame:
    """Compute task-difficulty context per ASP for Mountain profile."""
    mountain = df[df["profile"] == "mountain"]
    records = []
    for asp, grp in mountain.groupby("asp"):
        weather_high = (grp["weather_risk"] == "High").mean()
        access_difficult = (grp["site_access_difficulty"] == "Difficult").mean()
        records.append({
            "asp": asp,
            "avg_complexity": round(grp["task_complexity_score"].mean(), 2),
            "avg_travel_difficulty": round(grp["distance_to_site_km"].mean(), 1),
            "weather_exposure": round(weather_high * 100, 1),
            "access_restriction": round(access_difficult * 100, 1),
            "emergency_share": round(grp["emergency_task_flag"].mean() * 100, 1),
            "raw_sla": round(grp["completed_within_sla"].mean() * 100, 1),
            "raw_nps": round(grp["nps_score"].dropna().mean(), 1),
            "raw_repeat": round(grp["repeat_visit_required"].mean() * 100, 1),
            "raw_cost": round(grp["cost_per_task"].mean(), 1),
            "safety_score": max(0, 100 - int(grp["safety_incident_flag"].sum()) * 5),
            "n_tasks": len(grp),
        })
    ctx = pd.DataFrame(records)
    profile_avg_complexity = mountain["task_complexity_score"].mean()
    profile_avg_travel = mountain["distance_to_site_km"].mean()
    profile_avg_weather = (mountain["weather_risk"] == "High").mean() * 100
    profile_avg_access = (mountain["site_access_difficulty"] == "Difficult").mean() * 100
    ctx["complexity_ratio"] = (ctx["avg_complexity"] / profile_avg_complexity).round(2)
    ctx["travel_ratio"] = (ctx["avg_travel_difficulty"] / profile_avg_travel).round(2)
    ctx["weather_ratio"] = (ctx["weather_exposure"] / max(profile_avg_weather, 1)).round(2)
    ctx["access_ratio"] = (ctx["access_restriction"] / max(profile_avg_access, 1)).round(2)
    return ctx


def compute_raw_vs_adjusted_scores(ctx: pd.DataFrame, weights: dict, scored_df: pd.DataFrame = None) -> pd.DataFrame:
    """Compute raw overall score and causally-adjusted score.

    Step 1 (data only): adjusts based on task complexity and travel difficulty.
    Emergency share is NOT used here — that's SME knowledge (Step 2).
    """
    df = ctx.copy()

    if scored_df is not None:
        mountain_scored = scored_df[scored_df["profile"] == "mountain"].set_index("asp")
        df["raw_score"] = df["asp"].map(mountain_scored["business_score"]).round(1)
    else:
        df["sla_norm"] = _norm_direct(df["raw_sla"])
        df["nps_norm"] = _norm_direct(df["raw_nps"])
        df["repeat_norm"] = _norm_inverse(df["raw_repeat"])
        df["cost_norm"] = _norm_inverse(df["raw_cost"])
        df["safety_norm"] = _norm_direct(df["safety_score"])
        w = _norm_weights(weights)
        df["raw_score"] = (
            df["cost_norm"] * w["cost"] +
            df["safety_norm"] * w["safety"] +
            df["sla_norm"] * w["sla"] +
            df["nps_norm"] * w["nps"] +
            df["repeat_norm"] * w["repeat_visits"]
        ).round(1)

    # Step 1 causal adjustment: complexity + travel + weather + access (data-driven)
    df["causal_adjustment"] = (18 * (df["complexity_ratio"] - 1) + 8 * (df["travel_ratio"] - 1) + 6 * (df["weather_ratio"] - 1) + 6 * (df["access_ratio"] - 1)).round(1)
    df["adjusted_score_data"] = (df["raw_score"] + df["causal_adjustment"]).clip(0, 100).round(1)

    return df


def apply_sme_adjustment(ctx: pd.DataFrame, sme_observations: list[dict]) -> pd.DataFrame:
    """Apply SME observations (knowledge not in data) to further adjust scores."""
    ctx = ctx.copy()
    ctx["sme_adjustment"] = 0.0
    for obs in sme_observations:
        if obs["profile"] != "mountain":
            continue
        if obs["engine_effect"] == "emergency_expertise" and obs["asp"]:
            # Dispatcher knowledge: ASP handles emergency jobs (not visible in complexity alone)
            mask = ctx["asp"] == obs["asp"]
            ctx.loc[mask, "sme_adjustment"] += 10.0
        elif obs["engine_effect"] == "max_share_cap_45" and obs["asp"]:
            # Quality drops at high volume
            mask = ctx["asp"] == obs["asp"]
            ctx.loc[mask, "sme_adjustment"] -= 3.0
        elif obs["engine_effect"] == "weather_region_penalty" and obs["asp"]:
            # Regional weather prediction affects specific ASP
            mask = ctx["asp"] == obs["asp"]
            ctx.loc[mask, "sme_adjustment"] -= 8.0
    ctx["final_score"] = (ctx["adjusted_score_data"] + ctx["sme_adjustment"]).clip(0, 100).round(1)
    return ctx


def naive_vs_causal_decision(ctx: pd.DataFrame) -> dict:
    """Return narrative for naive vs causal decision based on actual data."""
    best_raw = ctx.loc[ctx["raw_score"].idxmax(), "asp"]
    worst_raw = ctx.loc[ctx["raw_score"].idxmin(), "asp"]
    best_final = ctx.loc[ctx["final_score"].idxmax(), "asp"]

    raw_ranking = ctx.sort_values("raw_score", ascending=False)["asp"].tolist()
    final_ranking = ctx.sort_values("final_score", ascending=False)["asp"].tolist()
    ranking_changed = raw_ranking != final_ranking

    worst_row = ctx[ctx["asp"] == worst_raw].iloc[0]
    naive_text = f"Reduce {worst_raw} volume (raw score: {worst_row['raw_score']:.1f}/100)."

    if ranking_changed:
        best_final_row = ctx[ctx["asp"] == best_final].iloc[0]
        causal_text = (f"{best_final} is strongest after adjustment "
                       f"(final score: {best_final_row['final_score']:.1f}/100). "
                       f"Keep {worst_raw} for difficult tasks but cap share at 45%.")
    else:
        gap_before = ctx["raw_score"].max() - ctx["raw_score"].min()
        gap_after = ctx["final_score"].max() - ctx["final_score"].min()
        causal_text = (f"Ranking unchanged, but gap narrowed from {gap_before:.0f} to {gap_after:.0f} points. "
                       f"{worst_raw} handles harder work — avoid excessive penalty.")

    return {
        "naive_best": best_raw,
        "naive_worst": worst_raw,
        "causal_best": best_final,
        "ranking_changed": ranking_changed,
        "naive_decision": naive_text,
        "causal_decision": causal_text,
    }


def _norm_direct(s: pd.Series) -> pd.Series:
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series(50.0, index=s.index)
    return ((s - mn) / (mx - mn) * 100).round(1)


def _norm_inverse(s: pd.Series) -> pd.Series:
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series(50.0, index=s.index)
    return ((mx - s) / (mx - mn) * 100).round(1)


def _norm_weights(weights: dict) -> dict:
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}
