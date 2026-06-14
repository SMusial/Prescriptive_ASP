"""Scenario engine and dynamic rebalancing."""
import copy
import yaml
from pathlib import Path

from src.data_generator import PROFILES


def load_scenario_templates() -> dict:
    p = Path(__file__).parent.parent / "config" / "scenario_templates.yaml"
    with open(p) as f:
        return yaml.safe_load(f)


def apply_scenario(scenario_name: str, base_settings: dict, scored_df=None) -> dict:
    """Return modified settings dict for the given scenario."""
    templates = load_scenario_templates()
    tpl = templates.get(scenario_name)
    if not tpl:
        return base_settings

    settings = copy.deepcopy(base_settings)

    # Weight overrides
    for k, v in tpl.get("weight_overrides", {}).items():
        settings["weights"][k] = v

    # Constraint overrides
    for k, v in tpl.get("constraint_overrides", {}).items():
        if k == "budget":
            settings["constraints"]["budget"] = v
        elif k == "mountain_weather":
            settings["constraints"]["mountain_weather"] = v
        elif k == "mountain_capacity_reduction":
            settings["constraints"]["mountain_capacity_reduction"] = v
        elif k == "climb_asp_2_certified":
            settings["constraints"]["climb_asp_2_certified"] = v

    return settings


def apply_rebalancing(scored_df, previous_allocation: dict, settings: dict) -> dict:
    """Apply dynamic rebalancing with movement caps."""
    max_change = settings.get("rebalancing", {}).get("max_change_per_cycle", 0.15)
    # For demo: simply return current allocation (rebalancing shown via scenario)
    return previous_allocation
