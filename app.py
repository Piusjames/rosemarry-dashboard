# app.py
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Rosemarry — African Startup Funding Insights", page_icon="🌹", layout="wide")

st.title("🌹 Rosemarry — African Startup Funding Insights (2018–2025)")
st.write("Interactive dashboard showing funding by country, industry, investors and growth over time.")

# --- CONFIG: Update these if you change username or repo name ---
GITHUB_USER = "piusjames"
REPO_NAME = "rosemarry-dashboard"
CSV_FILENAME = "africa_startup_funding_sample.csv"

CSV_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{CSV_FILENAME}"

@st.cache_data
def load_data(url):
    try:
        df = pd.read_csv(url)
    except Exception as e:
        st.error(f"Could not load CSV from GitHub. Check CSV_URL and repository. Error: {e}")
        st.stop()
    # normalize column names (allow some flexibility)
    df.columns = [c.strip() for c in df.columns]
    expected = ['year','country','industry','investor','amount_usd_millions']
    if not all(col in df.columns for col in expected):
        st.warning("CSV columns did not match expected. Expected columns: " + ", ".join(expected))
    # ensure numeric
    if 'amount_usd_millions' in df.columns:
        df['amount_usd_millions'] = pd.to_numeric(df['amount_usd_millions'], errors='coerce').fillna(0)
    if 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce').astype(int)
    return df

df = load_data(CSV_URL)

st.subheader("📌 Dataset Preview")
st.dataframe(df)

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(df['year'].dropna().unique().astype(int).tolist())
if years:
    year_range = st.sidebar.slider("Year range", min_value=min(years), max_value=max(years),
                                   value=(min(years), max(years)), step=1)
else:
    year_range = (2018, 2025)

countries = st.sidebar.multiselect("Countries", options=sorted(df['country'].dropna().unique()))
industries = st.sidebar.multiselect("Industries", options=sorted(df['industry'].dropna().unique()))
top_n = st.sidebar.slider("Top N investors", min_value=5, max_value=30, value=10)

# Apply filters
filtered = df.copy()
filtered = filtered[(filtered['year'] >= year_range[0]) & (filtered['year'] <= year_range[1])]
if countries:
    filtered = filtered[filtered['country'].isin(countries)]
if industries:
    filtered = filtered[filtered['industry'].isin(industries)]

st.markdown(f"### Showing **{len(filtered)}** deals from {year_range[0]} to {year_range[1]}")

# --- Total funding by country
st.subheader("🌍 Total funding by country")
country_funding = filtered.groupby('country', as_index=False)['amount_usd_millions'].sum().sort_values(by='amount_usd_millions', ascending=False)
if not country_funding.empty:
    chart1 = alt.Chart(country_funding).mark_bar().encode(
        x=alt.X('country:N', sort='-y'),
        y='amount_usd_millions:Q',
        tooltip=['country','amount_usd_millions']
    )
    st.altair_chart(chart1, use_container_width=True)
else:
    st.info("No country funding data to show for the selected filters.")

# --- Top industries
st.subheader("🏭 Top industries by funding")
industry_funding = filtered.groupby('industry', as_index=False)['amount_usd_millions'].sum().sort_values(by='amount_usd_millions', ascending=False)
if not industry_funding.empty:
    chart2 = alt.Chart(industry_funding).mark_bar().encode(
        x=alt.X('industry:N', sort='-y'),
        y='amount_usd_millions:Q',
        tooltip=['industry','amount_usd_millions']
    )
    st.altair_chart(chart2, use_container_width=True)
else:
    st.info("No industry data to show for the selected filters.")

# --- Top investors
st.subheader(f"🤝 Top {top_n} investors")
investor_funding = filtered.groupby('investor', as_index=False)['amount_usd_millions'].sum().sort_values(by='amount_usd_millions', ascending=False).head(top_n)
if not investor_funding.empty:
    chart3 = alt.Chart(investor_funding).mark_bar().encode(
        x=alt.X('investor:N', sort='-y'),
        y='amount_usd_millions:Q',
        tooltip=['investor','amount_usd_millions']
    )
    st.altair_chart(chart3, use_container_width=True)
else:
    st.info("No investor data to show for the selected filters.")

# --- Funding growth over time
st.subheader("📈 Funding growth over time")
timeline = filtered.groupby('year', as_index=False)['amount_usd_millions'].sum().sort_values(by='year')
if not timeline.empty:
    chart4 = alt.Chart(timeline).mark_line(point=True).encode(
        x='year:O',
        y='amount_usd_millions:Q',
        tooltip=['year','amount_usd_millions']
    )
    st.altair_chart(chart4, use_container_width=True)
else:
    st.info("No time-series data to show for the selected filters.")

st.write("---")
st.write("💡 **Rosemarry** — Powered by data, designed for Africa.")
