"""Plotly visualization helpers."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def allocation_bar_chart(allocations_pct: dict, allocations_abs: dict = None) -> go.Figure:
    """Stacked horizontal bar chart with ASP names and task counts on bars."""
    fig = go.Figure()
    profiles = ["urban", "mountain", "climb"]  # fixed order: Urban top, Climb bottom
    colors = {"1": "#90EE90", "2": "#636EFA", "3": "#EF553B"}

    for asp_num in ["1", "2", "3"]:
        x_vals = []
        y_vals = []
        text_vals = []
        for profile in reversed(profiles):  # reversed so Urban is on top in horizontal bar
            if profile not in allocations_pct:
                continue
            for asp, pct in allocations_pct[profile].items():
                if asp_num in asp:
                    x_vals.append(pct)
                    y_vals.append(profile.title())
                    abs_val = allocations_abs.get(profile, {}).get(asp, "") if allocations_abs else ""
                    text_vals.append(f"{asp.split(' ')[-2]} {asp.split(' ')[-1]}<br>{abs_val} ({pct:.0f}%)" if abs_val else f"{pct:.0f}%")
        fig.add_trace(go.Bar(name=f"ASP {asp_num}", x=x_vals, y=y_vals, orientation="h",
                             marker_color=colors[asp_num], text=text_vals, textposition="inside",
                             textfont=dict(size=11, color="black")))

    fig.update_layout(barmode="stack", height=250, margin=dict(l=20, r=20, t=20, b=20),
                      legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                      xaxis_title="Share (%)")
    return fig


def sla_comparison_chart(ctx: pd.DataFrame) -> go.Figure:
    """Grouped bar chart: raw SLA vs adjusted SLA for Mountain ASPs."""
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Raw SLA", x=ctx["asp"], y=ctx["raw_sla"], marker_color="#EF553B"))
    fig.add_trace(go.Bar(name="Adjusted SLA", x=ctx["asp"], y=ctx["adjusted_sla_data"], marker_color="#636EFA"))
    fig.update_layout(barmode="group", height=300, margin=dict(l=20, r=20, t=30, b=20),
                      yaxis_title="SLA %")
    return fig


def kpi_delta_card_data(scored_df: pd.DataFrame, allocations: dict) -> list[dict]:
    """Compute before/after KPI estimates for display."""
    # Before: equal split. After: optimized.
    profiles = scored_df["profile"].unique()
    before_cost, after_cost = 0, 0
    before_sla, after_sla = [], []
    before_nps, after_nps = [], []
    before_repeat, after_repeat = [], []

    for profile in profiles:
        pdf = scored_df[scored_df["profile"] == profile]
        n_asps = len(pdf)
        demand = sum(allocations.get(profile, {}).values())
        equal_share = demand / n_asps if n_asps else 0

        for _, row in pdf.iterrows():
            asp = row["asp"]
            alloc_tasks = allocations.get(profile, {}).get(asp, equal_share)
            before_cost += equal_share * row["smoothed_cost"]
            after_cost += alloc_tasks * row["smoothed_cost"]
            before_sla.append(row["smoothed_sla"])
            after_sla.append(row["smoothed_sla"])  # weighted later
            before_nps.append(row["smoothed_nps"])
            after_nps.append(row["smoothed_nps"])
            before_repeat.append(row["smoothed_repeat"])
            after_repeat.append(row["smoothed_repeat"])

    total_tasks = sum(sum(a.values()) for a in allocations.values())
    equal_total = total_tasks  # same total

    cards = [
        {"label": "Avg Cost/Task", "before": f"€{before_cost/equal_total:.0f}", "after": f"€{after_cost/total_tasks:.0f}"},
        {"label": "SLA Compliance", "before": f"{sum(before_sla)/len(before_sla):.0f}%", "after": f"{sum(after_sla)/len(after_sla):.0f}%"},
        {"label": "NPS", "before": f"{sum(before_nps)/len(before_nps):.0f}", "after": f"{sum(after_nps)/len(after_nps):.0f}"},
        {"label": "Repeat Visits", "before": f"{sum(before_repeat)/len(before_repeat):.1f}%", "after": f"{sum(after_repeat)/len(after_repeat):.1f}%"},
    ]
    return cards


def radar_chart(scored_df: pd.DataFrame, profile: str) -> go.Figure:
    """Radar chart comparing ASPs in a profile."""
    pdf = scored_df[scored_df["profile"] == profile].sort_values("asp")
    categories = ["Cost", "Safety", "SLA", "NPS", "Repeat Visits"]
    fig = go.Figure()
    for _, row in pdf.iterrows():
        # ASP 1 = light green, ASP 2 = blue, ASP 3 = red
        if "1" in row["asp"]:
            color = "#90EE90"
        elif "2" in row["asp"]:
            color = "#636EFA"
        else:
            color = "#EF553B"
        values = [row["cost_score"], row["safety_score_norm"], row["sla_score"],
                  row["nps_score_norm"], row["repeat_score"]]
        fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]],
                                       name=row["asp"], fill="toself",
                                       line=dict(color=color)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100],
                                                  tickfont=dict(color="orange"))),
                      height=350, margin=dict(l=40, r=40, t=20, b=60),
                      legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5))
    return fig
