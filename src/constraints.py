"""Constraints management for allocation engine."""


def build_constraints(settings: dict, sme_effects: dict, scored_df=None) -> dict:
    """Build full constraint set combining settings, SME effects, and scored data."""
    caps = dict(settings.get("capacity", {}))
    max_share = settings["constraints"]["max_share"]
    min_share = settings["constraints"]["min_share"]
    budget = settings["constraints"]["budget"]
    climb_safety = settings["constraints"]["climb_safety_threshold"]

    # Apply SME max share caps
    asp_max_share = {}
    for asp, cap in sme_effects.get("max_share_caps", {}).items():
        asp_max_share[asp] = min(cap, max_share)

    # Weather capacity reduction
    weather_reduction = 0.0
    if sme_effects.get("weather_capacity_reduction") and settings["constraints"].get("weather_impact"):
        weather_reduction = 0.20

    # Safety caution ASPs — reduce their max climb share
    safety_caution = sme_effects.get("safety_caution_asps", [])

    # Determine climb eligibility from scored_df
    climb_ineligible = []
    if scored_df is not None:
        climb_asps = scored_df[scored_df["profile"] == "climb"]
        for _, row in climb_asps.iterrows():
            if row["safety_score"] < climb_safety:
                climb_ineligible.append(row["asp"])
            if row["cert_coverage"] < 50:
                climb_ineligible.append(row["asp"])
        # Safety caution ASPs also get limited
        for asp in safety_caution:
            if asp not in climb_ineligible:
                asp_max_share[asp] = min(asp_max_share.get(asp, max_share), 0.25)

    return {
        "capacity": caps,
        "max_share": max_share,
        "min_share": min_share,
        "budget": budget,
        "climb_safety_threshold": climb_safety,
        "asp_max_share": asp_max_share,
        "weather_reduction": weather_reduction,
        "climb_ineligible": list(set(climb_ineligible)),
        "climb_repeat_penalty": sme_effects.get("climb_repeat_penalty", 1.0),
    }
