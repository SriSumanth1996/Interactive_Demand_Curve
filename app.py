import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt

# Load from Streamlit secrets (best practice)
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="iPhone 16 Demand", layout="centered")

st.title("📱 iPhone 16 Demand Survey")
st.markdown("**How much are you willing to pay for the iPhone 16?**")

# --- Input ---
price = st.number_input("Enter your price (₹)", min_value=10000, max_value=300000, step=500)

if st.button("Submit"):
    response = supabase.table("iphone_demand").insert({"price": int(price)}).execute()
    if response.data:
        st.success("✅ Your response has been recorded!")
    else:
        st.error("❌ Something went wrong.")

# --- Fetch and Plot Data ---
response = supabase.table("iphone_demand").select("*").execute()
df = pd.DataFrame(response.data)

if not df.empty:
    st.subheader("📊 Live Demand Histogram")
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("price:Q", bin=alt.Bin(maxbins=30), title="Price (₹)"),
            y=alt.Y("count()", title="Number of Students"),
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("📈 Summary Stats")
    st.write(f"Average WTP: ₹{df['price'].mean():,.0f}")
    st.write(f"Median WTP: ₹{df['price'].median():,.0f}")
    st.write(f"Most Common WTP: ₹{df['price'].mode()[0]:,.0f}")
else:
    st.info("No responses yet. Be the first!")
