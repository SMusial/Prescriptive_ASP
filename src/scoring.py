"""Multi-criteria scoring engine."""
import numpy as np
import pandas as pd


def compute_scores(metrics_df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """Compute weighted business scores normalized across ALL ASPs."""
    df = metrics_df.copy()
    # Normalize to 0-100 across all 9 ASPs (higher=better)
    df["cost_score"] = _normalize_inverse(df["smoothed_cost"])
    df["safety_score_norm"] = _normalize_direct(df["safety_score"])
    df["sla_score"] = _normalize_direct(df["smoothed_sla"])
    df["nps_score_norm"] = _normalize_direct(df["smoothed_nps"])
    df["repeat_score"] = _normalize_inverse(df["smoothed_repeat"])
    df["cert_score"] = _normalize_direct(df["cert_coverage"])

    w = _normalize_weights(weights)
    df["business_score"] = (
        df["cost_score"] * w["cost"]
        + df["safety_score_norm"] * w["safety"]
        + df["sla_score"] * w["sla"]
        + df["nps_score_norm"] * w["nps"]
        + df["repeat_score"] * w["repeat_visits"]
    ).round(1)
    return df


def _normalize_weights(weights: dict) -> dict:
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def _normalize_direct(series: pd.Series) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(50.0, index=series.index)
    return ((series - mn) / (mx - mn) * 100).round(1)


def _normalize_inverse(series: pd.Series) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(50.0, index=series.index)
    return ((mx - series) / (mx - mn) * 100).round(1)
