"""Constrained allocation optimizer."""
import numpy as np
import pandas as pd

from src.data_generator import PROFILES


def optimize_allocation(scored_df: pd.DataFrame, constraints: dict, demands: dict | None = None) -> dict:
    """Allocate tasks proportional to final scores, then apply constraints."""
    dems = demands or {p: v["demand"] for p, v in PROFILES.items()}
    results = {}
    total_cost = 0.0
    infeasible_reasons = []
    weeks_factor = constraints.get("planning_weeks", 4) / 4.0
    weather_by_profile = constraints.get("weather_reduction_by_profile", {})
    max_share = constraints["max_share"]
    min_share = constraints["min_share"]
    budget = constraints.get("budget", float("inf"))

    for profile, cfg in PROFILES.items():
        demand = dems.get(profile, cfg["demand"])
        asps = cfg["asps"]
        profile_scored = scored_df[scored_df["profile"] == profile].set_index("asp")
        allocation = {}

        # Filter eligible
        eligible = []
        for asp in asps:
            if profile == "climb" and asp in constraints.get("climb_ineligible", []):
                allocation[asp] = 0
                continue
            # Check capacity - ASPs with 0 capacity are blocked
            key = asp.lower().replace(" ", "_")
            raw_cap = constraints["capacity"].get(key, demand * 2)
            if raw_cap <= 0:
                allocation[asp] = 0
                continue
            eligible.append(asp)

        if not eligible:
            infeasible_reasons.append(f"{profile.title()}: No eligible ASPs.")
            results[profile] = {asp: 0 for asp in asps}
            continue

        # Capacity: scaled by planning weeks, reduced by weather
        cap = {}
        weather_red = weather_by_profile.get(profile, constraints.get("weather_reduction", 0))
        for asp in eligible:
            key = asp.lower().replace(" ", "_")
            raw_cap = int(constraints["capacity"].get(key, demand * 2) * weeks_factor)
            if weather_red > 0:
                raw_cap = int(raw_cap * (1 - weather_red))
            cap[asp] = raw_cap

        # Get scores for eligible ASPs
        scores = {}
        for asp in eligible:
            scores[asp] = profile_scored.loc[asp, "business_score"] if asp in profile_scored.index else 0

        # Step 1: Allocate proportional to score ratio (squared to amplify differences)
        score_total = sum(max(s, 1) ** 2 for s in scores.values())
        initial_alloc = {}
        for asp in eligible:
            proportion = max(scores[asp], 1) ** 2 / score_total
            initial_alloc[asp] = int(demand * proportion)

        # Step 1b: Winner bonus — top ASP gets +15%, 2nd gets +5%, last loses 20%
        sorted_by_score = sorted(eligible, key=lambda a: scores[a], reverse=True)
        if len(sorted_by_score) >= 2:
            initial_alloc[sorted_by_score[0]] += int(demand * 0.15)
            initial_alloc[sorted_by_score[1]] += int(demand * 0.05)
            bonus_total = int(demand * 0.15) + int(demand * 0.05)
            initial_alloc[sorted_by_score[-1]] = max(0, initial_alloc[sorted_by_score[-1]] - bonus_total)

        # Step 2: Apply constraints (clip to min_share, max_share, capacity, SME caps)
        for asp in eligible:
            sme_cap = constraints.get("asp_max_share", {}).get(asp, max_share)
            max_tasks = min(int(demand * min(max_share, sme_cap)), cap[asp])
            min_tasks = int(demand * min_share)
            allocation[asp] = max(min_tasks, min(initial_alloc[asp], max_tasks))

        # Step 3: Reconcile to match demand exactly
        allocated = sum(allocation[a] for a in eligible)
        diff = demand - allocated

        if diff > 0:
            # Under-allocated: give extra to highest-scored ASPs with room
            sorted_asps = sorted(eligible, key=lambda a: scores[a], reverse=True)
            for asp in sorted_asps:
                if diff <= 0:
                    break
                sme_cap = constraints.get("asp_max_share", {}).get(asp, max_share)
                max_tasks = min(int(demand * min(max_share, sme_cap)), cap[asp])
                room = max_tasks - allocation[asp]
                give = min(room, diff)
                allocation[asp] += give
                diff -= give
        elif diff < 0:
            # Over-allocated: reduce from lowest-scored ASPs
            sorted_asps = sorted(eligible, key=lambda a: scores[a])
            for asp in sorted_asps:
                if diff >= 0:
                    break
                min_tasks = int(demand * min_share)
                removable = allocation[asp] - min_tasks
                take = min(removable, -diff)
                allocation[asp] -= take
                diff += take

        if diff > 0:
            infeasible_reasons.append(
                f"{profile.title()}: {diff} tasks unallocated "
                f"(demand={demand}, total capacity={sum(cap.values())}).")

        # Add ineligible with 0
        for asp in asps:
            if asp not in allocation:
                allocation[asp] = 0

        # Cost
        for asp, tasks in allocation.items():
            if asp in profile_scored.index:
                total_cost += tasks * profile_scored.loc[asp, "smoothed_cost"]

        results[profile] = allocation

    # Budget check
    feasible = len(infeasible_reasons) == 0 and total_cost <= budget
    if total_cost > budget:
        infeasible_reasons.append(f"Total cost €{total_cost:,.0f} exceeds budget €{budget:,.0f} (over by €{total_cost - budget:,.0f}).")

    return {
        "allocations": results,
        "total_cost": round(total_cost, 0),
        "feasible": feasible,
        "infeasible_reasons": infeasible_reasons,
    }


def allocation_to_pct(allocations: dict, demands: dict | None = None) -> dict:
    """Convert task counts to percentages."""
    dems = demands or {p: v["demand"] for p, v in PROFILES.items()}
    pct = {}
    for profile, alloc in allocations.items():
        demand = dems.get(profile, sum(alloc.values()))
        if demand == 0:
            pct[profile] = {a: 0 for a in alloc}
        else:
            pct[profile] = {a: round(v / demand * 100, 1) for a, v in alloc.items()}
    return pct
