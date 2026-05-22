import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

sns.set_theme(style="whitegrid", palette="muted")


def _save(fig, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, f"{filename}.png")
    pdf_path = os.path.join(output_dir, f"{filename}.pdf")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def plot_top_makes_by_recall_count(df, output_dir):
    counts = df["make"].value_counts().head(10).sort_values()
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(counts.index, counts.values, color=sns.color_palette("muted", len(counts)))
    ax.set_xlabel("Number of Recalls")
    ax.set_title("Top 10 Vehicle Makes by Recall Count")
    for bar, val in zip(bars, counts.values):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2, str(val), va="center")
    _save(fig, output_dir, "top_makes_by_recall_count")


def plot_recalls_over_years(df, output_dir):
    df = df.copy()
    df["year"] = pd.to_numeric(df["modelYear"], errors="coerce")
    yearly = df.groupby("year").size().reset_index(name="count")
    yearly = yearly.dropna(subset=["year"])
    yearly["year"] = yearly["year"].astype(int)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(yearly["year"], yearly["count"], color=sns.color_palette("muted")[0], alpha=0.6, label="Recall Count")
    ax1.set_xlabel("Model Year")
    ax1.set_ylabel("Number of Recalls", color=sns.color_palette("muted")[0])
    ax1.tick_params(axis="y", labelcolor=sns.color_palette("muted")[0])

    ax2 = ax1.twinx()
    ax2.plot(yearly["year"], yearly["count"].rolling(3, min_periods=1).mean(),
             color=sns.color_palette("muted")[2], linewidth=2, marker="o", label="3-Year Rolling Avg")
    ax2.set_ylabel("Rolling Average", color=sns.color_palette("muted")[2])
    ax2.tick_params(axis="y", labelcolor=sns.color_palette("muted")[2])

    ax1.set_title("Recalls by Model Year with Rolling Average")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    _save(fig, output_dir, "recalls_over_years")


def plot_recall_distribution_by_component(df, output_dir):
    top_components = df["component"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_components.values, y=top_components.index, hue=top_components.index,
                palette="muted", ax=ax, legend=False)
    ax.set_xlabel("Number of Recalls")
    ax.set_title("Top 10 Components by Recall Frequency")
    _save(fig, output_dir, "recall_distribution_by_component")


def plot_rating_boxplot_by_make(df, output_dir):
    top_makes = df["make"].value_counts().head(6).index
    filtered = df[df["make"].isin(top_makes)].copy()
    filtered["year"] = pd.to_numeric(filtered["modelYear"], errors="coerce")
    filtered = filtered.dropna(subset=["year"])

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=filtered, x="make", y="year", hue="make", palette="muted", ax=ax, legend=False)
    ax.set_xlabel("Vehicle Make")
    ax.set_ylabel("Model Year")
    ax.set_title("Model Year Distribution by Make (Top 6)")
    _save(fig, output_dir, "year_boxplot_by_make")


def plot_recall_heatmap(df, output_dir):
    top_makes = df["make"].value_counts().head(8).index
    top_components = df["component"].value_counts().head(8).index
    filtered = df[df["make"].isin(top_makes) & df["component"].isin(top_components)]
    pivot = filtered.groupby(["make", "component"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax, linewidths=0.5)
    ax.set_title("Recall Heatmap: Make vs Component")
    ax.set_xlabel("Component")
    ax.set_ylabel("Make")
    _save(fig, output_dir, "recall_heatmap")


def plot_consequence_distribution(df, output_dir):
    df = df.copy()
    if "consequence_summary" in df.columns:
        col = "consequence_summary"
    else:
        col = df.columns[0]

    keywords = ["crash", "fire", "injury", "death", "loss", "failure"]
    counts = {kw: df[col].str.lower().str.contains(kw, na=False).sum() for kw in keywords}
    counts = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x=list(counts.keys()), y=list(counts.values()), hue=list(counts.keys()),
                palette="muted", ax=ax, legend=False)
    ax.set_xlabel("Consequence Keyword")
    ax.set_ylabel("Number of Recalls Mentioning Keyword")
    ax.set_title("Recall Consequence Keyword Frequency")
    _save(fig, output_dir, "consequence_distribution")


def plot_cumulative_recalls_over_time(df, output_dir):
    df = df.copy()
    df["year"] = pd.to_numeric(df["modelYear"], errors="coerce")
    yearly = df.groupby("year").size().reset_index(name="count").dropna(subset=["year"])
    yearly["year"] = yearly["year"].astype(int)
    yearly = yearly.sort_values("year")
    yearly["cumulative"] = yearly["count"].cumsum()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(yearly["year"], yearly["cumulative"], color=sns.color_palette("muted")[3],
            linewidth=2.5, marker="o")
    ax.fill_between(yearly["year"], yearly["cumulative"], alpha=0.15,
                    color=sns.color_palette("muted")[3])
    ax.set_xlabel("Model Year")
    ax.set_ylabel("Cumulative Recalls")
    ax.set_title("Cumulative Recalls Over Model Years")
    _save(fig, output_dir, "cumulative_recalls_over_time")


def plot_dashboard_subplots(df, output_dir):
    df = df.copy()
    df["year"] = pd.to_numeric(df["modelYear"], errors="coerce")

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle("Automotive Recall Dashboard", fontsize=16, fontweight="bold")

    # Panel [0,0] - Top makes
    counts = df["make"].value_counts().head(8).sort_values()
    axes[0, 0].barh(counts.index, counts.values, color=sns.color_palette("muted", len(counts)))
    axes[0, 0].set_title("Top Makes by Recall Count")
    axes[0, 0].set_xlabel("Recalls")

    # Panel [0,1] - Recalls per year
    yearly = df.groupby("year").size().reset_index(name="count").dropna(subset=["year"])
    yearly["year"] = yearly["year"].astype(int)
    axes[0, 1].bar(yearly["year"], yearly["count"], color=sns.color_palette("muted")[1], alpha=0.8)
    axes[0, 1].set_title("Recalls by Model Year")
    axes[0, 1].set_xlabel("Year")
    axes[0, 1].set_ylabel("Count")

    # Panel [1,0] - Top components
    top_comp = df["component"].value_counts().head(8).sort_values()
    axes[1, 0].barh(top_comp.index, top_comp.values, color=sns.color_palette("muted", len(top_comp)))
    axes[1, 0].set_title("Top Components by Recall Count")
    axes[1, 0].set_xlabel("Recalls")

    # Panel [1,1] - Cumulative
    yearly_sorted = yearly.sort_values("year")
    yearly_sorted["cumulative"] = yearly_sorted["count"].cumsum()
    axes[1, 1].plot(yearly_sorted["year"], yearly_sorted["cumulative"],
                    color=sns.color_palette("muted")[3], linewidth=2, marker="o")
    axes[1, 1].fill_between(yearly_sorted["year"], yearly_sorted["cumulative"],
                             alpha=0.15, color=sns.color_palette("muted")[3])
    axes[1, 1].set_title("Cumulative Recalls")
    axes[1, 1].set_xlabel("Year")

    plt.tight_layout()
    _save(fig, output_dir, "dashboard_subplots")
