import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta

st.set_page_config(page_title="Food Spend Tracker", layout="wide", page_icon="🍔")

# ── Colors ──────────────────────────────────────────────
BG       = "#0e1117"
CARD_BG  = "#1a1d23"
BORDER   = "#2d3748"
TEXT     = "#f1f5f9"
MUTED    = "#94a3b8"
BLUE     = "#3b82f6"
GREEN    = "#22c55e"
RED      = "#ef4444"
AMBER    = "#f59e0b"
PINK     = "#ec4899"

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    CARD_BG,
    "axes.edgecolor":    BORDER,
    "axes.labelcolor":   MUTED,
    "xtick.color":       MUTED,
    "ytick.color":       MUTED,
    "text.color":        TEXT,
    "grid.color":        BORDER,
    "grid.linestyle":    "--",
    "grid.alpha":        0.4,
    "font.size":         11,
})

# ── CSS ─────────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, .stApp {{ background-color: {BG} !important; color: {TEXT}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: #13151a !important;
    border-right: 1px solid {BORDER};
  }}
  [data-testid="stSidebar"] * {{ color: {TEXT} !important; }}

  /* KPI metric cards */
  [data-testid="metric-container"] {{
    background: {CARD_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
  }}
  [data-testid="metric-container"] label  {{ color: {MUTED} !important; font-size: 12px !important; }}
  [data-testid="stMetricValue"]           {{ color: {TEXT}  !important; font-size: 26px !important; font-weight: 600 !important; }}

  /* Section headings */
  h1 {{ font-size: 1.9rem !important; font-weight: 700 !important; color: {TEXT} !important; }}
  h2, h3 {{ color: {TEXT} !important; font-weight: 600 !important; }}

  /* Dividers */
  hr {{ border-color: {BORDER} !important; margin: 1rem 0 !important; }}

  /* Insight / alert boxes */
  [data-testid="stAlert"] {{
    border-radius: 10px !important;
    font-size: 13px !important;
  }}

  /* Multiselect pills */
  [data-baseweb="tag"] {{
    background-color: #1e40af !important;
    border-radius: 6px !important;
  }}

  /* Chart containers */
  [data-testid="stPlotlyChart"],
  [data-testid="stImage"] {{
    border-radius: 12px;
    overflow: hidden;
  }}
</style>
""", unsafe_allow_html=True)

# ── Helper: dark figure ──────────────────────────────────
def dark_fig(w=6, h=3.4):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    return fig, ax

# ── Load data ────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/food_orders_clean.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

df = load_data()

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.markdown(f"## 🎛️ Filters")
platforms = st.sidebar.multiselect(
    "Platform", df["platform"].unique(), default=df["platform"].unique()
)
period = st.sidebar.selectbox(
    "Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
)
days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90, "All Time": 9999}
cutoff = datetime.now() - timedelta(days=days_map[period])
fdf = df[df["platform"].isin(platforms) & (df["order_date"] >= cutoff)].copy()

# ── Header ───────────────────────────────────────────────
st.markdown("# 🍔 Food Spend & Health Intelligence Tracker")
st.markdown(
    f"<p style='color:{MUTED}; margin-top:-10px; font-size:14px;'>"
    "Understand what you're eating and spending — one order at a time</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── KPIs ─────────────────────────────────────────────────
total      = fdf["total_amount"].sum()
avg_val    = fdf["total_amount"].mean() if len(fdf) > 0 else 0
savings    = fdf["discount"].sum()
orders     = len(fdf)
junk       = fdf[fdf["health_category"] == "Unhealthy"]["total_amount"].sum()
unhealthy_pct = (junk / total * 100) if total > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Spent",     f"₹{total:,.0f}")
k2.metric("📦 Total Orders",    f"{orders}")
k3.metric("🍽️ Avg Order Value", f"₹{avg_val:,.0f}")
k4.metric("💸 Total Savings",   f"₹{savings:,.0f}")

# colour-top-border injection
st.markdown(f"""
<style>
  div[data-testid="column"]:nth-child(1) [data-testid="metric-container"]
    {{ border-top: 3px solid {BLUE} !important; }}
  div[data-testid="column"]:nth-child(2) [data-testid="metric-container"]
    {{ border-top: 3px solid {GREEN} !important; }}
  div[data-testid="column"]:nth-child(3) [data-testid="metric-container"]
    {{ border-top: 3px solid {AMBER} !important; }}
  div[data-testid="column"]:nth-child(4) [data-testid="metric-container"]
    {{ border-top: 3px solid {PINK} !important; }}
</style>
""", unsafe_allow_html=True)

st.divider()

# ── Row 2: Line chart + Donut ────────────────────────────
col1, col2 = st.columns([1.6, 1])

with col1:
    st.markdown("### 📈 Spend Over Time")
    daily = fdf.groupby("order_date")["total_amount"].sum().reset_index()
    fig, ax = dark_fig(7, 3.4)
    ax.plot(daily["order_date"], daily["total_amount"],
            color=BLUE, linewidth=2.5, zorder=3)
    ax.fill_between(daily["order_date"], daily["total_amount"],
                    alpha=0.12, color=BLUE)
    ax.set_xlabel("Date", fontsize=11, color=MUTED)
    ax.set_ylabel("Amount (₹)", fontsize=11, color=MUTED)
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("### 🥗 Healthy vs Unhealthy")
    health = fdf.groupby("health_category")["total_amount"].sum()
    color_map = {"Healthy": GREEN, "Moderate": AMBER, "Unhealthy": RED}
    colors = [color_map.get(c, BLUE) for c in health.index]
    fig, ax = dark_fig(4, 3.4)
    wedges, _, autotexts = ax.pie(
        health, labels=None, autopct="%1.1f%%",
        colors=colors, startangle=90,
        wedgeprops={"edgecolor": BG, "linewidth": 2.5},
        pctdistance=0.78,
    )
    for t in autotexts:
        t.set_color(TEXT); t.set_fontsize(11)
    ax.add_artist(plt.Circle((0, 0), 0.52, fc=BG))
    patches = [mpatches.Patch(color=color_map[k], label=k)
               for k in health.index if k in color_map]
    ax.legend(handles=patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.06), ncol=3,
              framealpha=0, fontsize=9, labelcolor=TEXT)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

st.divider()

# ── Row 3: Top restaurants + Platform + Meal time ────────
col1, col2, col3 = st.columns([1.4, 0.9, 0.9])

with col1:
    st.markdown("### 🏆 Top Restaurants")
    top = fdf.groupby("restaurant")["total_amount"].sum().nlargest(7).sort_values()
    fig, ax = dark_fig(6, 3.6)
    bars = ax.barh(top.index, top.values, color=BLUE, height=0.55,
                   edgecolor="none")
    for bar, val in zip(bars, top.values):
        ax.text(val + 30, bar.get_y() + bar.get_height() / 2,
                f"₹{val:,.0f}", va="center", fontsize=9, color=MUTED)
    ax.set_xlabel("Total Spend (₹)", fontsize=10, color=MUTED)
    ax.xaxis.grid(True); ax.yaxis.grid(False)
    ax.tick_params(axis="y", labelsize=10)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("### 📱 By Platform")
    plat = fdf["platform"].value_counts()
    plat_colors = [BLUE, AMBER, GREEN][: len(plat)]
    fig, ax = dark_fig(3.6, 3.6)
    wedges, _, autotexts = ax.pie(
        plat, labels=None, autopct="%1.0f%%",
        colors=plat_colors, startangle=90,
        wedgeprops={"edgecolor": BG, "linewidth": 2.5},
        pctdistance=0.75,
    )
    for t in autotexts:
        t.set_color(TEXT); t.set_fontsize(10)
    ax.add_artist(plt.Circle((0, 0), 0.48, fc=BG))
    patches = [mpatches.Patch(color=plat_colors[i], label=p)
               for i, p in enumerate(plat.index)]
    ax.legend(handles=patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.06), ncol=1,
              framealpha=0, fontsize=9, labelcolor=TEXT)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

with col3:
    st.markdown("### 🕐 Meal Time")
    meal_order  = ["Breakfast", "Lunch", "Snacks", "Dinner"]
    meal_colors = [AMBER, GREEN, BLUE, RED]
    meal = fdf["meal_time"].value_counts().reindex(meal_order).fillna(0)
    fig, ax = dark_fig(3.6, 3.6)
    bars = ax.bar(meal.index, meal.values, color=meal_colors,
                  width=0.55, edgecolor="none")
    for bar, val in zip(bars, meal.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5,
                str(int(val)), ha="center", fontsize=9, color=MUTED)
    ax.set_ylabel("Orders", fontsize=10, color=MUTED)
    ax.yaxis.grid(True); ax.xaxis.grid(False)
    plt.xticks(rotation=15, ha="right", fontsize=10)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

st.divider()

# ── Smart Insights ────────────────────────────────────────
st.markdown("### 🧠 Smart Insights")
top_rest  = (fdf.groupby("restaurant")["total_amount"].sum().idxmax()
             if len(fdf) > 0 else "N/A")
most_meal = fdf["meal_time"].value_counts().idxmax() if len(fdf) > 0 else "N/A"

i1, i2, i3 = st.columns(3)
i1.error(   f"🍔 **{unhealthy_pct:.1f}%** of your spend is on unhealthy food")
i2.warning( f"🏪 You spend the most at **{top_rest}**")
i3.info(    f"🕐 You order the most at **{most_meal}** time")

if junk > 1000:
    st.success(
        f"💡 Cook at home 2× a week and save approx ₹{junk * 0.3:,.0f}/month!"
    )

st.markdown("<br>", unsafe_allow_html=True)