import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pbi_agent import create_agent, ask, wants_dax

st.set_page_config(page_title="Power BI Dashboard Agent", page_icon="⚡", layout="wide")

# --- Generate realistic sample data ---
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    regions = ["North", "South", "East", "West", "Central"]
    products = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard"]
    categories = ["Electronics", "Accessories", "Furniture", "Software", "Services"]
    months = pd.date_range("2024-01-01", "2024-12-31", freq="MS")

    rows = []
    for month in months:
        for region in regions:
            for product in products:
                qty = np.random.randint(10, 200)
                price = np.random.choice([799, 599, 349, 249, 89])
                rows.append({
                    "Date": month,
                    "Region": region,
                    "Product": product,
                    "Category": np.random.choice(categories),
                    "Quantity": qty,
                    "Revenue": qty * price,
                    "Target": qty * price * np.random.uniform(0.85, 1.15),
                    "Cost": qty * price * np.random.uniform(0.4, 0.7),
                })
    df = pd.DataFrame(rows)
    df["Profit"] = df["Revenue"] - df["Cost"]
    df["Month"] = df["Date"].dt.strftime("%b %Y")
    df["MonthNum"] = df["Date"].dt.month
    return df

df = generate_sample_data()


def build_dashboard(question):
    q = question.lower()
    charts = []

    # --- KPI CARDS (always show) ---
    total_rev = df["Revenue"].sum()
    total_orders = df["Quantity"].sum()
    avg_order = total_rev / total_orders
    profit_margin = (df["Profit"].sum() / total_rev) * 100

    kpi_fig = go.Figure()
    kpi_fig.add_trace(go.Indicator(mode="number", value=total_rev,
        number={"prefix": "$", "valueformat": ",.0f"},
        title={"text": "Total Revenue"}, domain={"row": 0, "column": 0}))
    kpi_fig.add_trace(go.Indicator(mode="number", value=total_orders,
        number={"valueformat": ",.0f"},
        title={"text": "Total Units Sold"}, domain={"row": 0, "column": 1}))
    kpi_fig.add_trace(go.Indicator(mode="number", value=avg_order,
        number={"prefix": "$", "valueformat": ",.2f"},
        title={"text": "Avg Order Value"}, domain={"row": 0, "column": 2}))
    kpi_fig.add_trace(go.Indicator(mode="number", value=profit_margin,
        number={"suffix": "%", "valueformat": ".1f"},
        title={"text": "Profit Margin"}, domain={"row": 0, "column": 3}))
    kpi_fig.update_layout(
        grid={"rows": 1, "columns": 4, "pattern": "independent"},
        height=180, margin=dict(t=40, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    charts.append(("📊 Key Performance Indicators", kpi_fig))

    # --- REGION CHARTS ---
    if any(w in q for w in ["region", "area", "geography", "location", "state", "territory"]):
        reg = df.groupby("Region", as_index=False).agg({"Revenue": "sum", "Target": "sum", "Profit": "sum"})
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Revenue", x=reg["Region"], y=reg["Revenue"], marker_color="#636EFA"))
        fig.add_trace(go.Bar(name="Target", x=reg["Region"], y=reg["Target"], marker_color="#EF553B"))
        fig.update_layout(barmode="group", title="Revenue vs Target by Region",
            height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("📍 Regional Performance", fig))

        fig2 = px.treemap(reg, path=["Region"], values="Revenue", color="Profit",
            color_continuous_scale="RdYlGn", title="Revenue Distribution by Region")
        fig2.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        charts.append(("🗺️ Revenue Distribution", fig2))

    # --- PRODUCT / UNDERPERFORMING ---
    if any(w in q for w in ["product", "item", "underperform", "top", "best", "worst", "sku"]):
        prod = df.groupby("Product", as_index=False).agg({"Revenue": "sum", "Profit": "sum", "Quantity": "sum"})
        prod["ProfitMargin"] = (prod["Profit"] / prod["Revenue"] * 100).round(1)
        fig = px.bar(prod.sort_values("Revenue", ascending=True), x="Revenue", y="Product",
            orientation="h", color="ProfitMargin", color_continuous_scale="RdYlGn",
            title="Product Revenue & Profit Margin")
        fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("📦 Product Performance", fig))

    # --- TIME / TREND ---
    if any(w in q for w in ["trend", "month", "time", "growth", "over time", "quarter", "year"]):
        monthly = df.groupby("MonthNum", as_index=False).agg({"Revenue": "sum", "Profit": "sum"})
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly["Month"] = monthly["MonthNum"].apply(lambda x: month_names[x-1])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Revenue"], name="Revenue",
            mode="lines+markers", line=dict(color="#636EFA", width=3)))
        fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Profit"], name="Profit",
            mode="lines+markers", line=dict(color="#00CC96", width=3)))
        fig.update_layout(title="Monthly Revenue & Profit Trend", height=400,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("📈 Trends Over Time", fig))

    # --- FINANCIAL ---
    if any(w in q for w in ["financ", "revenue", "expense", "cost", "profit", "margin", "p&l"]):
        reg = df.groupby("Region", as_index=False).agg({"Revenue": "sum", "Cost": "sum", "Profit": "sum"})
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Revenue", x=reg["Region"], y=reg["Revenue"], marker_color="#636EFA"))
        fig.add_trace(go.Bar(name="Cost", x=reg["Region"], y=reg["Cost"], marker_color="#EF553B"))
        fig.add_trace(go.Bar(name="Profit", x=reg["Region"], y=reg["Profit"], marker_color="#00CC96"))
        fig.update_layout(barmode="group", title="Revenue vs Cost vs Profit by Region",
            height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("💰 Financial Breakdown", fig))

    # --- HR / ATTRITION ---
    if any(w in q for w in ["hr", "employee", "attrition", "headcount", "turnover", "hire", "retention"]):
        depts = ["Engineering", "Sales", "Marketing", "HR", "Finance"]
        hr_data = pd.DataFrame({
            "Department": depts,
            "Headcount": np.random.randint(50, 300, 5),
            "Attrition": np.random.uniform(5, 25, 5).round(1),
            "Avg Tenure": np.random.uniform(1.5, 6, 5).round(1)
        })
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Headcount", x=hr_data["Department"], y=hr_data["Headcount"], marker_color="#636EFA"))
        fig.add_trace(go.Scatter(name="Attrition %", x=hr_data["Department"], y=hr_data["Attrition"],
            mode="lines+markers", yaxis="y2", line=dict(color="#EF553B", width=3)))
        fig.update_layout(title="Headcount & Attrition by Department",
            yaxis2=dict(title="Attrition %", overlaying="y", side="right"),
            height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("👥 HR Overview", fig))

    # --- MARKETING ---
    if any(w in q for w in ["marketing", "campaign", "lead", "conversion", "ctr", "acquisition"]):
        campaigns = pd.DataFrame({
            "Campaign": ["Email Q1", "Social Media", "Google Ads", "Referral", "Content Marketing"],
            "Spend": [15000, 25000, 40000, 10000, 20000],
            "Leads": [300, 500, 800, 200, 350],
            "Conversions": [45, 60, 120, 50, 40]
        })
        campaigns["CPA"] = (campaigns["Spend"] / campaigns["Conversions"]).round(2)
        campaigns["ConvRate"] = (campaigns["Conversions"] / campaigns["Leads"] * 100).round(1)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Leads", x=campaigns["Campaign"], y=campaigns["Leads"], marker_color="#636EFA"))
        fig.add_trace(go.Bar(name="Conversions", x=campaigns["Campaign"], y=campaigns["Conversions"], marker_color="#00CC96"))
        fig.add_trace(go.Scatter(name="Conv Rate %", x=campaigns["Campaign"], y=campaigns["ConvRate"],
            mode="lines+markers", yaxis="y2", line=dict(color="#EF553B", width=3)))
        fig.update_layout(barmode="group", title="Campaign Performance",
            yaxis2=dict(title="Conversion Rate %", overlaying="y", side="right"),
            height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("📣 Marketing Performance", fig))

    # --- CUSTOMER SUPPORT ---
    if any(w in q for w in ["support", "ticket", "customer service", "helpdesk", "sla", "resolution"]):
        support = pd.DataFrame({
            "Priority": ["Critical", "High", "Medium", "Low"],
            "Open": [12, 45, 89, 120],
            "Resolved": [10, 38, 75, 115],
            "Avg Resolution Hrs": [2.5, 8, 24, 48]
        })
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Open", x=support["Priority"], y=support["Open"], marker_color="#EF553B"))
        fig.add_trace(go.Bar(name="Resolved", x=support["Priority"], y=support["Resolved"], marker_color="#00CC96"))
        fig.update_layout(barmode="group", title="Support Tickets by Priority",
            height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("🎧 Support Dashboard", fig))

    # --- DEFAULT: show region + trend if nothing specific matched ---
    if len(charts) == 1:
        reg = df.groupby("Region", as_index=False)["Revenue"].sum()
        fig = px.bar(reg, x="Region", y="Revenue", color="Revenue",
            color_continuous_scale="blues", title="Revenue by Region")
        fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("📍 Revenue by Region", fig))

        monthly = df.groupby("MonthNum", as_index=False)["Revenue"].sum()
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly["Month"] = monthly["MonthNum"].apply(lambda x: month_names[x-1])
        fig2 = px.line(monthly, x="Month", y="Revenue", markers=True, title="Monthly Revenue Trend")
        fig2.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"))
        charts.append(("📈 Monthly Trend", fig2))

    return charts


# --- UI ---
st.title("⚡ Power BI Dashboard Agent")
st.caption("Describe any dashboard in plain English → get a live preview + insights. Ask for 'DAX' or 'code' when you're ready to build it.")

@st.cache_resource
def load_agent():
    return create_agent()

with st.spinner("Loading AI agent..."):
    agent = load_agent()

with st.sidebar:
    st.header("💡 Try These Requests")
    examples = [
        "I want to see how sales are doing across regions",
        "Show me which products are underperforming",
        "Why are these products underperforming?",
        "Build me an HR dashboard to track employee attrition",
        "I need a financial dashboard showing revenue vs expenses",
        "Now give me the DAX measures for this dashboard",
    ]
    for q in examples:
        if st.button(q, key=q):
            st.session_state["user_input"] = q

    st.divider()
    st.markdown("""
    ### How it works
    💬 **By default**, you get a plain-English explanation of the dashboard,
    key insights to look for, and likely reasons behind the numbers.

    🧮 **Ask for DAX** (say "DAX", "measures", "code", or "implementation")
    and the agent will generate the full Power BI implementation guide.

    ---
    *Built with Ollama + LangChain + Plotly*
    *100% free, runs locally*
    """)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Describe the dashboard you need...")

if "user_input" in st.session_state:
    user_input = st.session_state.pop("user_input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Decide mode based on whether the user asked for DAX/code
    dax_mode = wants_dax(user_input)

    with st.chat_message("assistant"):
        # 1. Build live dashboard
        st.markdown("### 🖥️ Live Dashboard Preview")
        st.caption("Working preview using sample data.")
        charts = build_dashboard(user_input)
        for title, fig in charts:
            st.markdown(f"**{title}**")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # 2. AI response — explanation by default, DAX only if asked
        if dax_mode:
            st.markdown("### 📝 Power BI Implementation Guide")
            spinner_msg = "Generating DAX code and recommendations... (30-60 seconds)"
        else:
            st.markdown("### 💬 Dashboard Insights & Explanation")
            spinner_msg = "Analyzing the dashboard and gathering insights... (30-60 seconds)"

        with st.spinner(spinner_msg):
            response = ask(agent, user_input)
            st.markdown(response)

            # If we're in explain mode, gently nudge the user about DAX
            if not dax_mode:
                st.info("💡 When you're ready to build this in Power BI, ask for the "
                        "**DAX measures** or **code** and I'll generate the full implementation guide.")

    st.session_state.messages.append({"role": "assistant", "content": user_input})