import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os


def _save_html(fig, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{filename}.html")
    fig.write_html(path)


def interactive_recalls_by_make(df, output_dir):
    counts = df["make"].value_counts().head(15).reset_index()
    counts.columns = ["make", "recall_count"]

    fig = px.bar(
        counts,
        x="recall_count",
        y="make",
        orientation="h",
        title="Top 15 Vehicle Makes by Recall Count",
        labels={"recall_count": "Number of Recalls", "make": "Vehicle Make"},
        color="recall_count",
        color_continuous_scale="Blues",
        hover_data={"make": True, "recall_count": True},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    _save_html(fig, output_dir, "interactive_recalls_by_make")


def interactive_recalls_timeline(df, output_dir):
    df = df.copy()
    df["year"] = pd.to_numeric(df["modelYear"], errors="coerce")
    yearly = df.groupby(["year", "make"]).size().reset_index(name="recall_count")
    yearly = yearly.dropna(subset=["year"])
    yearly["year"] = yearly["year"].astype(int)
    top_makes = df["make"].value_counts().head(6).index
    yearly = yearly[yearly["make"].isin(top_makes)]

    fig = px.line(
        yearly,
        x="year",
        y="recall_count",
        color="make",
        title="Recall Trends Over Model Years by Make",
        labels={"year": "Model Year", "recall_count": "Number of Recalls", "make": "Make"},
        markers=True,
        hover_data={"year": True, "recall_count": True, "make": True},
    )
    fig.update_layout(hovermode="x unified")
    _save_html(fig, output_dir, "interactive_recalls_timeline")


def interactive_component_treemap(df, output_dir):
    df = df.copy()
    top_makes = df["make"].value_counts().head(6).index
    filtered = df[df["make"].isin(top_makes)]
    grouped = filtered.groupby(["make", "component"]).size().reset_index(name="recall_count")

    fig = px.treemap(
        grouped,
        path=["make", "component"],
        values="recall_count",
        title="Recall Distribution: Make → Component",
        color="recall_count",
        color_continuous_scale="Blues",
        hover_data={"recall_count": True},
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Recalls: %{value}<br>Parent: %{parent}<extra></extra>"
    )
    _save_html(fig, output_dir, "interactive_component_treemap")


def interactive_scatter_year_vs_count(df, output_dir):
    df = df.copy()
    df["year"] = pd.to_numeric(df["modelYear"], errors="coerce")
    grouped = df.groupby(["year", "make"]).size().reset_index(name="recall_count")
    grouped = grouped.dropna(subset=["year"])
    grouped["year"] = grouped["year"].astype(int)
    top_makes = df["make"].value_counts().head(8).index
    grouped = grouped[grouped["make"].isin(top_makes)]

    fig = px.scatter(
        grouped,
        x="year",
        y="recall_count",
        color="make",
        size="recall_count",
        title="Model Year vs Recall Count per Make",
        labels={"year": "Model Year", "recall_count": "Recall Count", "make": "Make"},
        hover_data={"year": True, "recall_count": True, "make": True},
    )
    fig.update_layout(hovermode="closest")
    _save_html(fig, output_dir, "interactive_scatter_year_vs_count")


def interactive_multi_layout(df, output_dir):
    df = df.copy()
    df["year"] = pd.to_numeric(df["modelYear"], errors="coerce")

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Top 10 Makes by Recall Count",
            "Recalls by Model Year",
            "Top 10 Components",
            "Cumulative Recalls Over Years",
        ],
    )

    # Panel [1,1] - Top makes bar
    make_counts = df["make"].value_counts().head(10)
    fig.add_trace(
        go.Bar(
            x=make_counts.values,
            y=make_counts.index,
            orientation="h",
            name="Makes",
            marker_color="steelblue",
            hovertemplate="Make: %{y}<br>Recalls: %{x}<extra></extra>",
        ),
        row=1, col=1,
    )

    # Panel [1,2] - Recalls per year
    yearly = df.groupby("year").size().reset_index(name="count").dropna(subset=["year"])
    yearly["year"] = yearly["year"].astype(int)
    fig.add_trace(
        go.Bar(
            x=yearly["year"],
            y=yearly["count"],
            name="Year",
            marker_color="cornflowerblue",
            hovertemplate="Year: %{x}<br>Recalls: %{y}<extra></extra>",
        ),
        row=1, col=2,
    )

    # Panel [2,1] - Top components
    comp_counts = df["component"].value_counts().head(10)
    fig.add_trace(
        go.Bar(
            x=comp_counts.values,
            y=comp_counts.index,
            orientation="h",
            name="Components",
            marker_color="mediumpurple",
            hovertemplate="Component: %{y}<br>Recalls: %{x}<extra></extra>",
        ),
        row=2, col=1,
    )

    # Panel [2,2] - Cumulative
    yearly_sorted = yearly.sort_values("year")
    yearly_sorted["cumulative"] = yearly_sorted["count"].cumsum()
    fig.add_trace(
        go.Scatter(
            x=yearly_sorted["year"],
            y=yearly_sorted["cumulative"],
            mode="lines+markers",
            name="Cumulative",
            line={"color": "tomato", "width": 2},
            hovertemplate="Year: %{x}<br>Cumulative: %{y}<extra></extra>",
        ),
        row=2, col=2,
    )

    fig.update_layout(
        height=800,
        title_text="Automotive Recall Interactive Dashboard",
        showlegend=False,
    )
    _save_html(fig, output_dir, "interactive_multi_layout")
