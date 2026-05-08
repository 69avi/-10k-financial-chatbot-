"""
engine.py  —  Financial Analysis Engine
Handles all query parsing, data analysis, and chart generation.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# ── Column aliases so users can ask naturally ─────────────────────────────────
COLUMN_MAP = {
    "revenue":            "Revenue",
    "net income":         "Net_Income",
    "income":             "Net_Income",
    "profit":             "Net_Income",
    "assets":             "Total_Assets",
    "total assets":       "Total_Assets",
    "liabilities":        "Total_Liabilities",
    "total liabilities":  "Total_Liabilities",
    "eps":                "EPS",
    "earnings per share": "EPS",
    "cash flow":          "Operating_Cash_Flow",
    "operating cash":     "Operating_Cash_Flow",
    "r&d":                "R&D_Expense",
    "research":           "R&D_Expense",
    "gross profit":       "Gross_Profit",
}

METRIC_LABELS = {
    "Revenue":              "Revenue ($M)",
    "Net_Income":           "Net Income ($M)",
    "Total_Assets":         "Total Assets ($M)",
    "Total_Liabilities":    "Total Liabilities ($M)",
    "EPS":                  "Earnings Per Share ($)",
    "Operating_Cash_Flow":  "Operating Cash Flow ($M)",
    "R&D_Expense":          "R&D Expense ($M)",
    "Gross_Profit":         "Gross Profit ($M)",
}


def fmt_val(col: str, val: float) -> str:
    """Format a value based on the metric type."""
    if col == "EPS":
        return f"${val:.2f}"
    return f"${val:,.0f}M"


def detect_companies(query: str, companies: list[str]) -> list[str]:
    """Return companies mentioned in query (case-insensitive)."""
    q = query.lower()
    return [c for c in companies if c.lower() in q]


def detect_metric(query: str) -> str | None:
    """Return the DataFrame column name for the metric in the query."""
    q = query.lower()
    for keyword, col in COLUMN_MAP.items():
        if keyword in q:
            return col
    return None


def detect_year(query: str) -> int | None:
    """Extract a 4-digit year from the query."""
    match = re.search(r"\b(20\d{2})\b", query)
    return int(match.group(1)) if match else None


# ── Core answer function ──────────────────────────────────────────────────────

def answer_query(query: str, df: pd.DataFrame) -> tuple[str, go.Figure | None]:
    """
    Parse a natural-language financial query and return (text_answer, chart).
    Returns (error_message, None) if the query can't be resolved.
    """
    q       = query.lower().strip()
    all_cos = df["Company"].unique().tolist()
    mentioned_cos = detect_companies(q, all_cos)
    metric  = detect_metric(q)
    year    = detect_year(q)

    # ── 1. Comparison between 2+ companies ───────────────────────────────────
    if len(mentioned_cos) >= 2:
        col = metric or "Revenue"
        label = METRIC_LABELS.get(col, col)
        sub = df[df["Company"].isin(mentioned_cos)].copy()

        if year:
            sub = sub[sub["Year"] == year]
            if sub.empty:
                return f"No data found for {year}.", None
            rows = sub[["Company", col]].set_index("Company")
            lines = "\n".join(
                f"  • {co}: {fmt_val(col, rows.loc[co, col])}"
                for co in mentioned_cos if co in rows.index
            )
            answer = f"**{label} comparison ({year}):**\n{lines}"
            fig = px.bar(
                sub, x="Company", y=col, color="Company",
                title=f"{label} — {year}",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
        else:
            answer = f"**{label} trend — {', '.join(mentioned_cos)}:**"
            fig = px.line(
                sub, x="Year", y=col, color="Company", markers=True,
                title=f"{label} Over Time",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        return answer, fig

    # ── 2. Single company queries ─────────────────────────────────────────────
    target_cos = mentioned_cos if mentioned_cos else all_cos

    # Growth / YoY change
    if any(w in q for w in ["growth", "change", "yoy", "increased", "decreased", "trend"]):
        col   = metric or "Revenue"
        label = METRIC_LABELS.get(col, col)
        sub   = df[df["Company"].isin(target_cos)].sort_values(["Company", "Year"])
        sub["YoY_Change"] = sub.groupby("Company")[col].pct_change() * 100
        sub   = sub.dropna(subset=["YoY_Change"])

        lines = []
        for co in sub["Company"].unique():
            rows = sub[sub["Company"] == co][["Year", "YoY_Change"]]
            for _, r in rows.iterrows():
                arrow = "▲" if r["YoY_Change"] > 0 else "▼"
                lines.append(f"  {co} {int(r['Year'])}: {arrow} {r['YoY_Change']:.1f}%")

        fig = px.bar(
            sub, x="Year", y="YoY_Change", color="Company", barmode="group",
            title=f"{label} — YoY Growth (%)",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        return f"**{label} — Year-over-Year Growth:**\n" + "\n".join(lines), fig

    # Profit margin
    if any(w in q for w in ["margin", "profitability"]):
        sub = df[df["Company"].isin(target_cos)].copy()
        sub["Profit_Margin_%"] = (sub["Net_Income"] / sub["Revenue"]) * 100
        lines = []
        for co in sub["Company"].unique():
            last = sub[sub["Company"] == co].sort_values("Year").iloc[-1]
            lines.append(f"  {co} ({int(last['Year'])}): {last['Profit_Margin_%']:.1f}%")
        fig = px.line(
            sub, x="Year", y="Profit_Margin_%", color="Company", markers=True,
            title="Net Profit Margin (%) Over Time",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        return "**Net Profit Margins (latest year):**\n" + "\n".join(lines), fig

    # Single metric lookup
    if metric:
        col   = metric
        label = METRIC_LABELS.get(col, col)
        sub   = df[df["Company"].isin(target_cos)].sort_values(["Company", "Year"])

        if year:
            sub = sub[sub["Year"] == year]
            if sub.empty:
                return f"No data for {year}.", None
            lines = "\n".join(
                f"  • {r['Company']}: {fmt_val(col, r[col])}"
                for _, r in sub.iterrows()
            )
            fig = px.bar(
                sub, x="Company", y=col, color="Company",
                title=f"{label} — {year}",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
        else:
            latest = sub.sort_values("Year").groupby("Company").last().reset_index()
            lines  = "\n".join(
                f"  • {r['Company']} ({int(r['Year'])}): {fmt_val(col, r[col])}"
                for _, r in latest.iterrows()
            )
            fig = px.line(
                sub, x="Year", y=col, color="Company", markers=True,
                title=f"{label} Over Time",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        return f"**{label}:**\n{lines}", fig

    # Dashboard / summary
    if any(w in q for w in ["summary", "overview", "dashboard", "all", "show"]):
        return _build_summary(df, target_cos)

    # Best / worst
    if any(w in q for w in ["best", "top", "highest", "most"]):
        col   = metric or "Revenue"
        label = METRIC_LABELS.get(col, col)
        latest = df.sort_values("Year").groupby("Company").last().reset_index()
        best   = latest.loc[latest[col].idxmax()]
        return (
            f"**Highest {label}:**\n"
            f"  🏆 {best['Company']} ({int(best['Year'])}): {fmt_val(col, best[col])}",
            None,
        )

    if any(w in q for w in ["worst", "lowest", "least"]):
        col   = metric or "Net_Income"
        label = METRIC_LABELS.get(col, col)
        latest = df.sort_values("Year").groupby("Company").last().reset_index()
        worst  = latest.loc[latest[col].idxmin()]
        return (
            f"**Lowest {label}:**\n"
            f"  📉 {worst['Company']} ({int(worst['Year'])}): {fmt_val(col, worst[col])}",
            None,
        )

    # Fallback
    return (
        "I couldn't parse that query. Try asking about:\n"
        "• **Revenue**, **net income**, **EPS**, **profit margin**\n"
        "• **Compare Apple and Tesla**\n"
        "• **Revenue growth** or **YoY change**\n"
        "• **Best revenue**, **lowest net income**\n"
        "• **Summary** or **overview**",
        None,
    )


def _build_summary(df: pd.DataFrame, companies: list[str]) -> tuple[str, go.Figure]:
    """Build a 4-panel overview chart."""
    sub = df[df["Company"].isin(companies)]
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["Revenue ($M)", "Net Income ($M)", "EPS ($)", "Profit Margin (%)"],
    )
    colors = px.colors.qualitative.Bold
    for i, co in enumerate(companies):
        c   = sub[sub["Company"] == co].sort_values("Year")
        clr = colors[i % len(colors)]
        base = dict(x=c["Year"], name=co, legendgroup=co, line=dict(color=clr))
        margin = (c["Net_Income"] / c["Revenue"] * 100).values
        fig.add_trace(go.Scatter(**base, y=c["Revenue"],   showlegend=True),  row=1, col=1)
        fig.add_trace(go.Scatter(**base, y=c["Net_Income"],showlegend=False), row=1, col=2)
        fig.add_trace(go.Scatter(**base, y=c["EPS"],       showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(**base, y=margin,         showlegend=False), row=2, col=2)

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_text="Financial Overview Dashboard",
        height=550,
    )
    return "**Financial Overview Dashboard** — key metrics across all companies:", fig


def get_sample_questions(companies: list[str]) -> list[str]:
    """Return context-aware example questions based on loaded companies."""
    if len(companies) >= 2:
        c1, c2 = companies[0], companies[1]
        return [
            f"Compare {c1} and {c2} revenue",
            f"What is {c1}'s net income growth?",
            f"Show revenue trend for all companies",
            f"Which company has the highest profit margin?",
            f"Compare {c1} and {c2} EPS in 2023",
            f"What is {c1}'s R&D expense?",
            "Show me a summary dashboard",
            "Which company has the best net income?",
        ]
    return [
        "What is the total revenue?",
        "Show net income growth",
        "What is the profit margin?",
        "Show summary dashboard",
    ]
