# ------------------ IMPORT LIBRARIES ------------------
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# ------------------ PAGE CONFIGURATION ------------------
st.set_page_config(page_title=" PhonePe Insights Dashboard", layout="wide")
st.title(" PhonePe Insights Dashboard")
st.markdown("### Developed by **Aakash Shinde** | SQL + Streamlit + Plotly")

# ------------------ DATABASE CONNECTION ------------------
try:
    engine = create_engine("mssql+pyodbc://DESKTOP-7J2KD1H\\AAKASH/phonepay?driver=ODBC+Driver+17+for+SQL+Server")
    st.sidebar.success(" Connected to SQL Server Database")
except Exception as e:
    st.sidebar.error(f" Database connection failed: {e}")
    st.stop()

# ------------------ SIDEBAR MENU ------------------
menu = st.sidebar.radio(
    " Select Dataset",
    [
        "Aggregated Transaction",
        "Aggregated User",
        "Aggregated Insurance",
        "Top Transaction",
        "Top User",
        "Top Insurance",
    ],
)

# ------------------ LOAD DATA FUNCTION ------------------
@st.cache_data
def load_data(query):
    """Load SQL table into a Pandas DataFrame."""
    return pd.read_sql(query, engine)

# ------------------ FILTER FUNCTION ------------------
def filter_data(df):
    """Sidebar filters for year, quarter, and state."""
    years = sorted(df['year'].unique())
    quarters = sorted(df['quarter'].unique())
    states = sorted(df['state'].unique())

    year_selected = st.sidebar.selectbox(" Select Year", ["All"] + list(years))
    quarter_selected = st.sidebar.selectbox("🗓 Select Quarter", ["All"] + list(quarters))
    state_selected = st.sidebar.selectbox(" Select State", ["All"] + list(states))

    filtered = df.copy()
    if year_selected != "All":
        filtered = filtered[filtered['year'] == year_selected]
    if quarter_selected != "All":
        filtered = filtered[filtered['quarter'] == quarter_selected]
    if state_selected != "All":
        filtered = filtered[filtered['state'] == state_selected]

    return filtered

# ============================================================
#  AGGREGATED TRANSACTION TABLE
# ============================================================
if menu == "Aggregated Transaction":
    st.header(" Aggregated Transaction Analysis")
    df = load_data("SELECT * FROM aggregated_transaction")
    data = filter_data(df)

    # KPI METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", f"{data['count'].sum():,.0f}")
    col2.metric("Total Amount (₹)", f"{data['amount'].sum()/1e7:.2f} Cr")
    avg_value = data['amount'].sum() / data['count'].sum() if data['count'].sum() > 0 else 0
    col3.metric("Avg. Transaction Value (₹)", f"{avg_value:,.0f}")

    # VISUAL 1: Transaction Type Distribution (Pie Chart)
    st.subheader(" Transaction Share by Type")
    type_data = data.groupby('type')['amount'].sum().reset_index()
    fig = px.pie(type_data, names='type', values='amount', title="Share by Transaction Type", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    # VISUAL 2: Yearly Growth Trend (Line Chart)
    st.subheader(" Yearly Transaction Growth")
    trend = data.groupby('year')['amount'].sum().reset_index()
    fig2 = px.line(trend, x='year', y='amount', markers=True, title="Yearly Transaction Growth")
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
#  AGGREGATED USER TABLE
# ============================================================
elif menu == "Aggregated User":
    st.header(" Aggregated User Analysis")
    df = load_data("SELECT * FROM aggregated_user")
    data = filter_data(df)

    # VISUAL 1: Device Brand Usage (Bar Chart)
    if 'brand' in data.columns and 'percentage' in data.columns:
        st.subheader("📱 Top Device Brands by User Percentage")
        brand = data.groupby('brand')['percentage'].mean().reset_index().sort_values(by='percentage', ascending=False).head(10)
        fig = px.bar(brand, x='brand', y='percentage', color='brand', title="Device Brand Share")
        st.plotly_chart(fig, use_container_width=True)

        # VISUAL 2: Brand Share (Pie Chart)
        st.subheader(" Device Brand Share (Pie Chart)")
        fig_pie = px.pie(brand, names='brand', values='percentage', hole=0.4, title="Device Brand Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

    # VISUAL 3: User Count by Year (Line Chart)
    if 'count' in data.columns:
        st.subheader(" Yearly User Growth Trend")
        year_data = data.groupby('year')['count'].sum().reset_index()
        fig2 = px.line(year_data, x='year', y='count', markers=True, title="User Growth Over Time")
        st.plotly_chart(fig2, use_container_width=True)

# ============================================================
#  AGGREGATED INSURANCE TABLE
# ============================================================
elif menu == "Aggregated Insurance":
    st.header(" Aggregated Insurance Analysis")
    df = load_data("SELECT * FROM aggregated_insurance")
    data = filter_data(df)

    # VISUAL 1: Top States by Insurance Value (Bar Chart)
    st.subheader(" Top States by Insurance Transaction Value")
    state_ins = data.groupby('state')['amount'].sum().reset_index().sort_values(by='amount', ascending=False).head(10)
    fig = px.bar(state_ins, x='state', y='amount', color='state', title="Top States by Insurance Value")
    st.plotly_chart(fig, use_container_width=True)

    # VISUAL 2: Insurance Value Distribution (Pie Chart)
    st.subheader(" Insurance Value Distribution (Top 10 States)")
    fig_pie = px.pie(state_ins, names='state', values='amount', hole=0.4, title="Insurance Value Share by State")
    st.plotly_chart(fig_pie, use_container_width=True)

    # VISUAL 3: Yearly Growth (Line Chart)
    st.subheader(" Insurance Growth Over Years")
    trend = data.groupby('year')['amount'].sum().reset_index()
    fig2 = px.line(trend, x='year', y='amount', markers=True, title="Yearly Insurance Growth")
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
#  TOP TRANSACTION TABLE
# ============================================================
elif menu == "Top Transaction":
    st.header(" Top Transaction Analysis")
    df = load_data("SELECT * FROM top_transaction")
    data = filter_data(df)

    st.subheader("Top States by Transaction Amount")
    state_txn = data.groupby('state')['amount'].sum().reset_index().sort_values(by='amount', ascending=False).head(10)
    fig = px.bar(state_txn, x='state', y='amount', color='state', title="Top 10 States by Transaction Value")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Districts by Transaction Amount")
    dist_txn = data.groupby('entity_name')['amount'].sum().reset_index().sort_values(by='amount', ascending=False).head(10)
    fig2 = px.bar(dist_txn, x='entity_name', y='amount', color='entity_name', title="Top 10 Districts by Transaction Value")
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
#  TOP USER TABLE
# ============================================================
elif menu == "Top User":
    st.header(" Top User Analysis")
    df = load_data("SELECT * FROM top_user")
    data = filter_data(df)

    st.subheader(" Top States by Registered Users")
    if 'registeredUsers' in data.columns:
        users = data.groupby('state')['registeredUsers'].sum().reset_index().sort_values(by='registeredUsers', ascending=False).head(10)
        fig = px.bar(users, x='state', y='registeredUsers', color='state', title="Top States by Registered Users")
    else:
        users = data.groupby('state')['count'].sum().reset_index().sort_values(by='count', ascending=False).head(10)
        fig = px.bar(users, x='state', y='count', color='state', title="Top States by User Count")
    st.plotly_chart(fig, use_container_width=True)

    if 'pincode' in data.columns:
        st.subheader("Top Pincodes by Users")
        if 'registeredUsers' in data.columns:
            pin = data.groupby('pincode')['registeredUsers'].sum().reset_index().sort_values(by='registeredUsers', ascending=False).head(10)
            fig2 = px.bar(pin, x='pincode', y='registeredUsers', color='pincode', title="Top Pincodes by Registered Users")
        else:
            pin = data.groupby('pincode')['count'].sum().reset_index().sort_values(by='count', ascending=False).head(10)
            fig2 = px.bar(pin, x='pincode', y='count', color='pincode', title="Top Pincodes by User Count")
        st.plotly_chart(fig2, use_container_width=True)

# ============================================================
#  TOP INSURANCE TABLE
# ============================================================
elif menu == "Top Insurance":
    st.header(" Top Insurance Analysis")
    df = load_data("SELECT * FROM top_insurance")
    data = filter_data(df)

    st.subheader("Top States by Insurance Transaction Value")
    state_ins = data.groupby('state')['amount'].sum().reset_index().sort_values(by='amount', ascending=False).head(10)
    fig = px.bar(state_ins, x='state', y='amount', color='state', title="Top 10 States by Insurance Value")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Districts by Insurance Transaction Value")
    dist_ins = data.groupby('entity_name')['amount'].sum().reset_index().sort_values(by='amount', ascending=False).head(10)
    fig2 = px.bar(dist_ins, x='entity_name', y='amount', color='entity_name', title="Top 10 Districts by Insurance Value")
    st.plotly_chart(fig2, use_container_width=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown(" Data Source: PhonePe Pulse |  Dashboard Created by **Aakash Shinde**")