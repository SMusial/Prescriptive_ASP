"""SME observation layer."""
from datetime import date

SME_OBSERVATIONS = [
    {
        "note_id": "SME-001",
        "source_role": "Safety Manager",
        "profile": "climb",
        "asp": "SkyClimb",
        "business_observation": "SkyClimb recently changed two senior supervisors. Formal audit is still valid, but operational confidence is lower for high-risk sites.",
        "confidence_level": "Medium",
        "valid_from": "2026-05-01",
        "valid_until": "2026-08-01",
        "engine_effect": "temporary_safety_caution",
    },
    {
        "note_id": "SME-002",
        "source_role": "Dispatcher",
        "profile": "mountain",
        "asp": "AlpineReach",
        "business_observation": "AlpineReach consistently handles the most complex emergency escalations — their technicians have the deepest incident-resolution expertise across all task categories.",
        "confidence_level": "High",
        "valid_from": "2026-01-01",
        "valid_until": "2026-12-31",
        "engine_effect": "emergency_expertise",
    },
    {
        "note_id": "SME-003",
        "source_role": "Operations Manager",
        "profile": "mountain",
        "asp": "AlpineReach",
        "business_observation": "AlpineReach quality drops when share exceeds 45% because they rely more on subcontractors.",
        "confidence_level": "High",
        "valid_from": "2026-01-01",
        "valid_until": "2026-12-31",
        "engine_effect": "max_share_cap_45",
    },
    {
        "note_id": "SME-004",
        "source_role": "Contract Manager",
        "profile": "climb",
        "asp": None,
        "business_observation": "Repeat visits for Climb tasks have greater reputational impact than Urban repeat visits.",
        "confidence_level": "High",
        "valid_from": "2026-01-01",
        "valid_until": "2026-12-31",
        "engine_effect": "climb_repeat_penalty_multiplier",
    },
    {
        "note_id": "SME-005",
        "source_role": "Regional Expert",
        "profile": "mountain",
        "asp": "AlpinGmbH",
        "business_observation": "AlpinGmbH delivery performance was significantly affected by flooding in 2 districts where AlpinGmbH has the highest task concentration last quarter — road closures and site access issues caused major delays.",
        "confidence_level": "High",
        "valid_from": "2026-05-01",
        "valid_until": "2026-10-01",
        "engine_effect": "weather_region_penalty",
    },
]


def get_active_observations(ref_date: date | None = None) -> list[dict]:
    """Return SME observations active on given date."""
    ref = ref_date or date.today()
    active = []
    for obs in SME_OBSERVATIONS:
        if date.fromisoformat(obs["valid_from"]) <= ref <= date.fromisoformat(obs["valid_until"]):
            active.append(obs)
    return active


def get_engine_effects(observations: list[dict]) -> dict:
    """Translate active observations into engine constraint modifiers."""
    effects = {
        "max_share_caps": {},
        "safety_caution_asps": [],
        "climb_repeat_penalty": 1.0,
        "weather_capacity_reduction": False,
    }
    for obs in observations:
        eff = obs["engine_effect"]
        if eff == "max_share_cap_45":
            effects["max_share_caps"][obs["asp"]] = 0.45
        elif eff == "temporary_safety_caution":
            effects["safety_caution_asps"].append(obs["asp"])
        elif eff == "climb_repeat_penalty_multiplier":
            effects["climb_repeat_penalty"] = 1.5
        elif eff == "weather_capacity_reduction":
            effects["weather_capacity_reduction"] = True
    return effects
