
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8002/analytics/summary"

st.set_page_config(
    page_title="Frugal AI | Cost Intelligence",
    page_icon="📊",
    layout="wide",
)

st.title("Frugal AI")
st.caption("AI Infrastructure Cost Intelligence")


@st.cache_data(ttl=10)
def fetch_analytics():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    return response.json()


if st.button("Refresh metrics"):
    fetch_analytics.clear()

try:
    data = fetch_analytics()
except requests.RequestException:
    st.error(
        "Unable to connect to the analytics API. "
        "Check that FastAPI is running on port 8002."
    )
    st.stop()


st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Requests",
    f"{data['total_requests']:,}",
)

col2.metric(
    "Actual LLM Cost",
    f"${data['total_actual_cost']:.6f}",
)

col3.metric(
    "Attributed Savings",
    f"${data['total_savings']:.6f}",
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Cache Hit Rate",
    f"{data['cache_hit_rate']:.1f}%",
)

col5.metric(
    "Routing Rate",
    f"{data['routing_rate']:.1f}%",
)

col6.metric(
    "Average Provider Latency",
    f"{data['average_provider_latency_ms']:.0f} ms",
)

st.divider()

st.subheader("Cost Optimization")

st.metric(
    "Savings Against Recorded Baselines",
    f"{data['savings_percentage']:.2f}%",
)

st.info(
    "Savings are estimated using recorded model-pricing "
    "baselines. Historical requests without valid "
    "baselines are excluded from the savings percentage. "
    "Metrics currently reflect development test data."
)

st.caption("Data source: Frugal AI Analytics API")