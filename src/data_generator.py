"""Synthetic task-level data generator for the ASP allocation demo."""
import numpy as np
import pandas as pd


PROFILES = {
    "urban": {"demand": 1200, "asps": ["CityConnect", "UrbanLink", "StreetNet"]},
    "mountain": {"demand": 420, "asps": ["AlpineReach", "SummitField", "AlpinGmbH"]},
    "climb": {"demand": 160, "asps": ["SkyClimb", "TowerPro", "VerticalWorks"]},
}

# ASP characteristic templates: (cost_mean, sla_rate, nps_mean, repeat_rate, safety_score, complexity_bias, emergency_share)
ASP_TEMPLATES = {
    "CityConnect": (75, 0.86, -10, 0.10, 80, 0.35, 0.08),
    "UrbanLink": (125, 0.95, 35, 0.04, 88, 0.50, 0.12),
    "StreetNet": (100, 0.82, -15, 0.13, 76, 0.70, 0.06),
    "AlpineReach": (120, 0.87, 35, 0.06, 75, 0.85, 0.45),
    "SummitField": (100, 0.93, 5, 0.04, 90, 0.35, 0.08),
    "AlpinGmbH": (140, 0.84, -10, 0.12, 82, 0.50, 0.18),
    "SkyClimb": (130, 0.78, -5, 0.14, 70, 0.75, 0.20),
    "TowerPro": (170, 0.91, 20, 0.05, 93, 0.40, 0.08),
    "VerticalWorks": (200, 0.93, 25, 0.03, 97, 0.50, 0.06),
}


def generate_tasks(seed: int = 42, demands: dict | None = None,
                   variance: float = 0.5, n_weeks: int = 4) -> pd.DataFrame:
    """Generate synthetic task-level DataFrame."""
    rng = np.random.default_rng(seed)
    rows = []
    task_id = 0
    dems = demands or {p: v["demand"] for p, v in PROFILES.items()}

    for profile, cfg in PROFILES.items():
        demand = dems.get(profile, cfg["demand"])
        asps = cfg["asps"]
        # biased assignment
        weights = _assignment_weights(profile)
        asp_assignments = rng.choice(asps, size=demand, p=weights)

        for i, asp in enumerate(asp_assignments):
            task_id += 1
            t = ASP_TEMPLATES[asp]
            cost_mean, sla_rate, nps_mean, repeat_rate, safety, complexity_bias, emergency_share = t
            week = int(rng.integers(1, n_weeks + 1))
            is_emergency = rng.random() < emergency_share
            complexity = min(1.0, max(0.0, rng.beta(2, 2) * complexity_bias + (0.2 if is_emergency else 0)))
            distance = round(rng.exponential(15 if profile == "mountain" else 8 if profile == "climb" else 5), 1)
            travel = round(distance * rng.uniform(1.5, 3.0), 1)
            weather = rng.choice(["Low", "Medium", "High"], p=_weather_probs(profile))
            access = rng.choice(["Easy", "Moderate", "Difficult"], p=[0.5, 0.3, 0.2] if profile == "urban" else [0.2, 0.4, 0.4])
            security = rng.random() < (0.15 if profile == "mountain" else 0.05)
            cert_required = profile == "climb" or (profile == "mountain" and is_emergency)
            cert_available = rng.random() < (0.95 if "ASP 3" in asp and profile == "climb" else 0.85)
            fatigue = rng.random() < 0.1
            escalation = rng.random() < 0.08
            segment = rng.choice(["Residential", "Business", "Enterprise"], p=[0.6, 0.3, 0.1])
            sla_class = rng.choice(["Standard", "Priority", "Critical"], p=[0.6, 0.3, 0.1])
            # outcomes — variance scales noise
            sla_penalty = (0.05 * complexity + 0.03 * (weather == "High") + 0.05 * is_emergency) * (0.5 + variance)
            completed_sla = rng.random() < (sla_rate - sla_penalty)
            cost = max(40, round(rng.normal(cost_mean * (1 + 0.3 * complexity), cost_mean * 0.15 * (0.5 + variance)), 2))
            repeat = rng.random() < (repeat_rate + 0.04 * complexity * (0.5 + variance))
            nps = _generate_nps(rng, nps_mean, i, demand, variance)
            safety_incident = rng.random() < (0.02 if safety > 85 else 0.06) * (0.5 + variance)
            confidence = round(rng.uniform(0.3, 1.0), 2)

            rows.append({
                "task_id": task_id, "week": week, "profile": profile,
                "region": f"{profile.title()} Region {rng.integers(1,4)}",
                "asp": asp, "task_type": _task_type(profile, rng),
                "task_complexity_score": round(complexity, 2),
                "estimated_job_duration": round(rng.uniform(0.5, 4.0) * (1 + complexity), 1),
                "distance_to_site_km": distance, "travel_time_minutes": travel,
                "weather_risk": weather, "site_access_difficulty": access,
                "security_restriction": security, "required_certification": cert_required,
                "asp_certified_staff_available": cert_available,
                "technician_fatigue_risk": fatigue, "manual_escalation_flag": escalation,
                "emergency_task_flag": is_emergency, "customer_segment": segment,
                "sla_class": sla_class, "cost_per_task": cost,
                "completed_within_sla": completed_sla, "repeat_visit_required": repeat,
                "nps_score": nps, "safety_incident_flag": safety_incident,
                "data_confidence_score": confidence,
            })

    df = pd.DataFrame(rows)
    # inject missing values
    df = _inject_missing(df, rng)
    return df


def _assignment_weights(profile: str) -> list:
    if profile == "mountain":
        return [0.50, 0.30, 0.20]  # ASP1 gets much more (harder) work
    if profile == "climb":
        return [0.25, 0.35, 0.40]
    return [0.30, 0.45, 0.25]


def _weather_probs(profile: str) -> list:
    if profile == "mountain":
        return [0.3, 0.4, 0.3]
    if profile == "climb":
        return [0.4, 0.4, 0.2]
    return [0.6, 0.3, 0.1]


def _task_type(profile: str, rng) -> str:
    types = {"urban": ["Installation", "Repair", "Maintenance", "Upgrade"],
             "mountain": ["Installation", "Repair", "Emergency Repair", "Line Maintenance"],
             "climb": ["Tower Climb", "Antenna Install", "Height Inspection", "Cable Replacement"]}
    return rng.choice(types[profile])


def _generate_nps(rng, mean, idx, total, variance=0.5):
    if rng.random() < (0.10 + 0.16 * variance):  # more missing with higher variance
        return np.nan
    return int(np.clip(rng.normal(mean, 20 + 20 * variance), -100, 100))


def generate_workforce(seed: int = 42) -> dict:
    """Generate workforce split (senior/regular/junior ratio) per ASP.

    Senior: experienced, certified, can handle all tasks.
    Regular: standard technicians.
    Junior: entry-level, supervised work only.
    Ratios sum to 100% per ASP.
    """
    import numpy as np
    rng = np.random.default_rng(seed)

    # Profile-level typical ratios
    profile_ratios = {
        "urban": (15, 55, 30),     # few seniors needed
        "mountain": (30, 50, 20),  # more seniors for difficult access
        "climb": (50, 35, 15),     # mostly seniors for safety
    }

    # Map ASP name to profile
    asp_to_profile = {}
    for p, cfg in PROFILES.items():
        for a in cfg["asps"]:
            asp_to_profile[a] = p

    workforce = {}
    for asp in ASP_TEMPLATES:
        profile = asp_to_profile.get(asp, "urban")
        base_s, base_r, base_j = profile_ratios[profile]
        s = max(5, int(base_s + rng.integers(-8, 9)))
        j = max(5, int(base_j + rng.integers(-5, 6)))
        r = 100 - s - j
        workforce[asp] = {"senior": s, "regular": r, "junior": j}
    return workforce


def _inject_missing(df: pd.DataFrame, rng) -> pd.DataFrame:
    # additional sparse missingness
    mask = rng.random(len(df)) < 0.05
    df.loc[mask, "data_confidence_score"] = np.nan
    return df
