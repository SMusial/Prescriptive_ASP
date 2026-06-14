"""Explanation / reason code generator."""
import pandas as pd


def generate_reason_codes(profile: str, allocation: dict, scored_df: pd.DataFrame, constraints: dict) -> dict[str, list[str]]:
    """Generate reason codes for each ASP's allocation in a profile."""
    profile_df = scored_df[scored_df["profile"] == profile].set_index("asp")
    reasons = {}
    for asp, tasks in allocation.items():
        codes = []
        if asp not in profile_df.index:
            reasons[asp] = ["Not scored"]
            continue
        row = profile_df.loc[asp]

        if tasks == 0:
            if asp in constraints.get("climb_ineligible", []):
                codes.append("- Ineligible: safety or certification below threshold")
            else:
                codes.append("- Zero allocation due to constraints")
            reasons[asp] = codes
            continue

        # Positive reasons
        if row["business_score"] == profile_df["business_score"].max():
            codes.append("+ Highest overall business score")
        if row["safety_score"] >= 90:
            codes.append("+ Strong safety score")
        if row["sla_score"] >= 70:
            codes.append("+ Good SLA performance")
        if row["nps_score_norm"] >= 70:
            codes.append("+ High customer satisfaction")
        if row["cert_coverage"] >= 90:
            codes.append("+ Strong certified workforce")
        if row["repeat_score"] >= 70:
            codes.append("+ Low repeat visit rate")

        # Negative reasons
        if row["cost_score"] < 30:
            codes.append("- Higher cost than alternatives")
        if row["smoothed_sla"] < profile_df["smoothed_sla"].mean():
            codes.append("- Raw SLA below profile average (check causal context)")
        cap = constraints.get("asp_max_share", {}).get(asp)
        if cap:
            codes.append(f"- Capped at {int(cap*100)}% due to SME quality observation")

        if not codes:
            codes.append("+ Balanced allocation")
        reasons[asp] = codes
    return reasons


def generate_infeasibility_suggestions(reasons: list[str]) -> list[str]:
    """Generate suggested actions for infeasibility."""
    suggestions = []
    for r in reasons:
        if "budget" in r.lower():
            suggestions.append("Increase budget by 10-15%")
        if "capacity" in r.lower() or "unallocated" in r.lower():
            suggestions.append("Relax max ASP share from 60% to 70%")
            suggestions.append("Add certified capacity")
        if "eligible" in r.lower():
            suggestions.append("Review certification requirements")
    return suggestions or ["Review constraints and adjust priorities"]
