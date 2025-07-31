import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt

# --- Load from Streamlit secrets ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="iPhone 16 Demand", layout="centered")

st.title("📱 iPhone 16 Demand Survey")
st.markdown("**How much are you willing to pay for the iPhone 16?**")

# --- Input Section ---
price = st.number_input("Enter your price (₹)", min_value=50000, max_value=200000, step=500)

submitted = False
if st.button("Submit"):
    response = supabase.table("iphone_demand").insert({"price": int(price)}).execute()
    if response.data:
        st.success("✅ Your response has been recorded!")
        submitted = True
    else:
        st.error("❌ Something went wrong.")

# --- Fetch Data ---
response = supabase.table("iphone_demand").select("*").execute()
df = pd.DataFrame(response.data)

# --- Define histogram bins from ₹50,000 to ₹200,000 in ₹500 intervals ---
bin_edges = list(range(50000, 200500, 500))
bin_labels = [f"{b}-{b+499}" for b in bin_edges[:-1]]

# --- Prepare Histogram Data ---
if not df.empty:
    df["bin"] = pd.cut(df["price"], bins=bin_edges, labels=bin_labels, right=False)
    histogram = (
        df["bin"]
        .value_counts()
        .sort_index()
        .reindex(bin_labels, fill_value=0)
        .reset_index()
    )
    histogram.columns = ["range", "count"]
else:
    histogram = pd.DataFrame({"range": bin_labels, "count": [0]*len(bin_labels)})

# --- Plot Histogram with custom tick labels every ₹10k ---
xticks = [f"{i:,}" for i in range(50000, 200001, 10000)]

st.subheader("📊 Live Demand Histogram")
chart = (
    alt.Chart(histogram)
    .mark_bar()
    .encode(
        x=alt.X("range:N", title="Price Range (₹)", sort=bin_labels, axis=alt.Axis(values=xticks, labelAngle=-45)),
        y=alt.Y("count:Q", title="Number of Students"),
    )
    .properties(height=400)
)
st.altair_chart(chart, use_container_width=True)

# --- Stats Section ---
if not df.empty:
    st.subheader("📈 Summary Stats")
    st.write(f"Average WTP: ₹{df['price'].mean():,.0f}")
    st.write(f"Median WTP: ₹{df['price'].median():,.0f}")
    st.write(f"Most Common WTP: ₹{df['price'].mode()[0]:,.0f}")
else:
    if submitted:
        st.info("Fetching updated data...")
    else:
        st.info("Waiting for the first submission...")
