# app/streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

st.set_page_config(page_title="🍔 Food Spend Tracker", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/food_orders_clean.csv")
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

df = load_data()

# ─── SIDEBAR ───────────────────────────────────────────
st.sidebar.title("🎛️ Filters")
platform = st.sidebar.multiselect("Platform", df['platform'].unique(),
                                   default=df['platform'].unique())
period = st.sidebar.selectbox("Time Period",
                               ["Last 7 Days", "Last 30 Days",
                                "Last 90 Days", "All Time"])

period_map = {"Last 7 Days": 7, "Last 30 Days": 30,
              "Last 90 Days": 90, "All Time": 9999}
days = period_map[period]
cutoff = datetime.now() - timedelta(days=days)

filtered = df[(df['platform'].isin(platform)) &
              (df['order_date'] >= cutoff)]

# ─── HEADER ────────────────────────────────────────────
st.title("🍔 Food Spend & Health Intelligence Tracker")
st.markdown("*Understand what you're eating and spending — one order at a time*")
st.divider()

# ─── KPI CARDS ─────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Spent", f"₹{filtered['total_amount'].sum():,.0f}")
col2.metric("📦 Total Orders", len(filtered))
col3.metric("🍽️ Avg Order Value", f"₹{filtered['total_amount'].mean():,.0f}")
col4.metric("💸 Total Savings", f"₹{filtered['discount'].sum():,.0f}")

st.divider()

# ─── HEALTH BREAKDOWN ──────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥗 Healthy vs Unhealthy Spend")
    health_spend = filtered.groupby('health_category')['total_amount'].sum()
    colors = {'Healthy': '#2ecc71', 'Moderate': '#f39c12', 'Unhealthy': '#e74c3c'}
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(health_spend, labels=health_spend.index, autopct='%1.1f%%',
           colors=[colors[c] for c in health_spend.index],
           startangle=90)
    ax.set_facecolor('none')
    fig.patch.set_alpha(0)
    st.pyplot(fig)

with col2:
    st.subheader("📈 Spend Over Time")
    daily_spend = filtered.groupby('order_date')['total_amount'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(daily_spend['order_date'], daily_spend['total_amount'],
            color='#3498db', linewidth=2)
    ax.fill_between(daily_spend['order_date'], daily_spend['total_amount'],
                    alpha=0.2, color='#3498db')
    plt.xticks(rotation=45)
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount (₹)")
    fig.patch.set_alpha(0)
    st.pyplot(fig)

st.divider()

# ─── TOP RESTAURANTS ───────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Restaurants by Spend")
    top_rest = filtered.groupby('restaurant')['total_amount'].sum().nlargest(5)
    fig, ax = plt.subplots(figsize=(6, 4))
    top_rest.sort_values().plot(kind='barh', ax=ax, color='#9b59b6')
    ax.set_xlabel("Total Spend (₹)")
    fig.patch.set_alpha(0)
    st.pyplot(fig)

with col2:
    st.subheader("🕐 When Do You Order Most?")
    meal_counts = filtered['meal_time'].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4))
    meal_counts.plot(kind='bar', ax=ax,
                     color=['#e67e22','#3498db','#2ecc71','#e74c3c'])
    ax.set_xlabel("Meal Time")
    ax.set_ylabel("Number of Orders")
    plt.xticks(rotation=0)
    fig.patch.set_alpha(0)
    st.pyplot(fig)

st.divider()

# ─── SMART INSIGHTS ────────────────────────────────────
st.subheader("🧠 Smart Insights")

total = filtered['total_amount'].sum()
unhealthy_pct = (filtered[filtered['health_category']=='Unhealthy']['total_amount'].sum() / total * 100) if total > 0 else 0
top_restaurant = filtered.groupby('restaurant')['total_amount'].sum().idxmax() if len(filtered) > 0 else "N/A"
junk_spend = filtered[filtered['health_category']=='Unhealthy']['total_amount'].sum()

i1, i2, i3 = st.columns(3)
i1.info(f"🍔 **{unhealthy_pct:.1f}%** of your spend goes to unhealthy food")
i2.warning(f"🏪 You spend the most at **{top_restaurant}**")
i3.error(f"⚠️ ₹{junk_spend:,.0f} spent on junk food in this period")

# Cooking suggestion
if junk_spend > 2000:
    st.success(f"💡 **Tip:** Cook at home just 2x a week and save approx ₹{junk_spend*0.3:,.0f}/month!")