"""Data quality assessment and Bayesian smoothing."""
import numpy as np
import pandas as pd


def assess_quality(df: pd.DataFrame) -> dict:
    """Return data quality summary metrics."""
    nps_missing = df["nps_score"].isna().mean()
    total = len(df)
    # Low sample: ASP groups with < 30 tasks
    groups = df.groupby(["profile", "asp"]).size()
    low_sample_pct = (groups < 30).mean()
    # Outliers across key numeric columns
    outlier_count = sum(_count_outliers(df, c) for c in ["cost_per_task", "nps_score", "task_complexity_score"])
    # Safety sparsity: ratio of safety incidents to total (sparse if < 3%)
    safety_rate = df["safety_incident_flag"].mean()
    safety_sparsity = "High" if safety_rate < 0.02 else ("Medium" if safety_rate < 0.05 else "Low")
    # Overall confidence: composite of missingness, sample size, and sparsity
    miss_score = 1 - nps_missing
    sample_score = 1 - low_sample_pct
    safety_score = min(1.0, safety_rate / 0.05)
    composite = miss_score * 0.4 + sample_score * 0.3 + safety_score * 0.3
    overall = "High" if composite > 0.7 else ("Medium" if composite > 0.4 else "Low")

    return {
        "missing_nps_pct": round(nps_missing * 100, 1),
        "low_sample_pct": round(low_sample_pct * 100, 1),
        "outlier_count": outlier_count,
        "safety_sparsity": safety_sparsity,
        "overall_confidence": overall,
    }


def smooth_metrics(df: pd.DataFrame, strength: float = 10.0) -> pd.DataFrame:
    """Apply Bayesian smoothing to ASP-level KPIs.

    Handles missing values and outliers using empirical Bayes:
    - Missing values: excluded from observed mean; smoothing pulls toward profile baseline
      proportional to how few observations exist (fewer obs → stronger pull to baseline).
    - Outliers: winsorized to 5th/95th percentile BEFORE computing observed mean,
      preventing extreme values from distorting the estimate. Then Bayesian smoothing
      further stabilizes small/noisy samples.
    """
    records = []
    for (profile, asp), grp in df.groupby(["profile", "asp"]):
        n = len(grp)

        # NPS: winsorize then smooth (missing already excluded by dropna)
        nps_vals = grp["nps_score"].dropna()
        profile_nps = df[df["profile"] == profile]["nps_score"].dropna()
        raw_nps = nps_vals.mean() if len(nps_vals) > 0 else np.nan
        winsorized_nps = _winsorize(nps_vals)
        obs_nps = winsorized_nps.mean() if len(winsorized_nps) > 0 else np.nan
        baseline_nps = _winsorize(profile_nps).mean() if len(profile_nps) > 0 else 0
        smoothed_nps = _bayesian_smooth(obs_nps, len(nps_vals), baseline_nps, strength)

        # SLA
        raw_sla = grp["completed_within_sla"].mean() * 100
        baseline_sla = df[df["profile"] == profile]["completed_within_sla"].mean() * 100
        smoothed_sla = _bayesian_smooth(raw_sla, n, baseline_sla, strength)

        # Repeat visits
        raw_repeat = grp["repeat_visit_required"].mean() * 100
        baseline_repeat = df[df["profile"] == profile]["repeat_visit_required"].mean() * 100
        smoothed_repeat = _bayesian_smooth(raw_repeat, n, baseline_repeat, strength)

        # Cost: winsorize then smooth
        cost_vals = grp["cost_per_task"]
        profile_cost = df[df["profile"] == profile]["cost_per_task"]
        raw_cost = cost_vals.mean()
        obs_cost = _winsorize(cost_vals).mean()
        baseline_cost = _winsorize(profile_cost).mean()
        smoothed_cost = _bayesian_smooth(obs_cost, n, baseline_cost, strength)

        # Safety score
        safety_incidents = grp["safety_incident_flag"].sum()
        safety_score = max(0, 100 - safety_incidents * 5)

        # Certification coverage
        cert_coverage = grp["asp_certified_staff_available"].mean() * 100

        # Confidence label based on NPS responses + overall data completeness
        completeness = 1 - grp["nps_score"].isna().mean()
        confidence = _confidence_label(len(nps_vals), n, completeness)

        records.append({
            "profile": profile, "asp": asp, "n_tasks": n,
            "raw_nps": round(raw_nps, 1) if not np.isnan(raw_nps) else None,
            "smoothed_nps": round(smoothed_nps, 1),
            "nps_responses": len(nps_vals),
            "raw_sla": round(raw_sla, 1), "smoothed_sla": round(smoothed_sla, 1),
            "raw_cost": round(raw_cost, 1), "smoothed_cost": round(smoothed_cost, 1),
            "raw_repeat": round(raw_repeat, 1), "smoothed_repeat": round(smoothed_repeat, 1),
            "safety_score": safety_score, "cert_coverage": round(cert_coverage, 1),
            "confidence": confidence,
        })
    return pd.DataFrame(records)


def _bayesian_smooth(observed, n, baseline, strength):
    """Empirical Bayes shrinkage: smoothed = (obs*n + baseline*k) / (n+k).

    With few observations, result is pulled toward the baseline.
    With many observations, result stays close to the observed value.
    """
    if np.isnan(observed) or n == 0:
        return baseline
    return (observed * n + baseline * strength) / (n + strength)


def _winsorize(series: pd.Series, lower=0.05, upper=0.95) -> pd.Series:
    """Clip values to percentile bounds to reduce outlier influence."""
    if len(series) < 5:
        return series
    lo = series.quantile(lower)
    hi = series.quantile(upper)
    return series.clip(lo, hi)


def _confidence_label(n_responses: int, n_tasks: int, completeness: float) -> str:
    """Composite confidence: sample size + data completeness."""
    if n_responses >= 30 and completeness > 0.7 and n_tasks >= 50:
        return "High"
    if n_responses >= 10 and completeness > 0.5:
        return "Medium"
    return "Low"


def _count_outliers(df: pd.DataFrame, col: str) -> int:
    s = df[col].dropna()
    if len(s) < 10:
        return 0
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
