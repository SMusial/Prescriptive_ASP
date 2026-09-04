"""Tests for the ASP Allocation Demo."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from src.data_generator import generate_tasks, PROFILES
from src.data_quality import assess_quality, smooth_metrics
from src.scoring import compute_scores
from src.constraints import build_constraints
from src.optimizer import optimize_allocation, allocation_to_pct
from src.sme_layer import get_active_observations, get_engine_effects


def test_data_generator_columns():
    df = generate_tasks(seed=42)
    required = ["task_id", "week", "profile", "asp", "cost_per_task",
                "completed_within_sla", "repeat_visit_required", "nps_score",
                "safety_incident_flag", "task_complexity_score", "emergency_task_flag"]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"


def test_no_time_of_delivery_kpi():
    df = generate_tasks(seed=42)
    assert "time_of_delivery" not in df.columns
    assert "actual_delivery_time" not in df.columns


def test_missing_values_generated():
    df = generate_tasks(seed=42)
    assert df["nps_score"].isna().sum() > 0


def test_smoothing_stable():
    df = generate_tasks(seed=42)
    metrics = smooth_metrics(df)
    assert (metrics["smoothed_nps"] >= -100).all()
    assert (metrics["smoothed_nps"] <= 100).all()


def test_scores_range():
    df = generate_tasks(seed=42)
    metrics = smooth_metrics(df)
    weights = {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10}
    scored = compute_scores(metrics, weights)
    assert (scored["business_score"] >= 0).all()
    assert (scored["business_score"] <= 100).all()


def test_climb_ineligible_gets_zero():
    df = generate_tasks(seed=42)
    metrics = smooth_metrics(df)
    weights = {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10}
    scored = compute_scores(metrics, weights)
    climb_asps = PROFILES["climb"]["asps"]
    ineligible = climb_asps[0]
    constraints = {
        "capacity": {a.lower().replace(" ", "_"): 200 for a in climb_asps},
        "max_share": 0.60, "min_share": 0.10,
        "budget": 180000, "climb_safety_threshold": 90,
        "asp_max_share": {}, "weather_reduction": 0,
        "climb_ineligible": [ineligible],
        "climb_repeat_penalty": 1.0,
    }
    result = optimize_allocation(scored, constraints)
    assert result["allocations"]["climb"][ineligible] == 0


def test_budget_constraint():
    df = generate_tasks(seed=42)
    metrics = smooth_metrics(df)
    weights = {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10}
    scored = compute_scores(metrics, weights)
    constraints = {
        "capacity": {a.lower().replace(" ", "_"): 9999 for p in PROFILES.values() for a in p["asps"]},
        "max_share": 0.60, "min_share": 0.10,
        "budget": 50000, "climb_safety_threshold": 90,
        "asp_max_share": {}, "weather_reduction": 0,
        "climb_ineligible": [], "climb_repeat_penalty": 1.0,
    }
    result = optimize_allocation(scored, constraints)
    # Should flag budget infeasibility
    assert not result["feasible"] or result["total_cost"] <= 50000


def test_sme_cap_respected():
    df = generate_tasks(seed=42)
    metrics = smooth_metrics(df)
    weights = {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10}
    scored = compute_scores(metrics, weights)
    obs = get_active_observations()
    effects = get_engine_effects(obs)
    assert "AlpineReach" in effects["max_share_caps"]
    assert effects["max_share_caps"]["AlpineReach"] == 0.45


def test_scenario_changes_output():
    df = generate_tasks(seed=42)
    metrics = smooth_metrics(df)
    w1 = {"cost": 20, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10}
    w2 = {"cost": 40, "safety": 30, "sla": 25, "nps": 15, "repeat_visits": 10}
    s1 = compute_scores(metrics, w1)
    s2 = compute_scores(metrics, w2)
    assert not s1["business_score"].equals(s2["business_score"])
