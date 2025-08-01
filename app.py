import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt
# Load from Streamlit secrets
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
st.set_page_config(page_title="iPhone 16 Demand", layout="centered")
st.title("📱 iPhone 16 Demand Survey")
st.markdown("**How much are you willing to pay for the iPhone 16?**")
st.markdown("""
**📝 Please Note:**
1. Please enter the amount only once
2. Enter the amount in steps of 1000 i.e., 65000, 66000...
3. Min 50000 to Max 150000
""")
# --- Input Section ---
price = st.number_input("Enter your price (₹)", min_value=50000, max_value=150000, step=1000)
submitted = False
if st.button("Submit"):
    response = supabase.table("iphone_demand").insert({"price": int(price)}).execute()
    if response.data:
        st.success("✅ Your response has been recorded!")
        submitted = True
    else:
        st.error("❌ Something went wrong.")
# --- Fetch Data After Submission ---
response = supabase.table("iphone_demand").select("*").execute()
df = pd.DataFrame(response.data)
if not df.empty:
    st.subheader("📊 Live Demand Histogram")
    
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("price:Q", 
                   title="Price (₹)",
                   axis=alt.Axis(labelAngle=-90, format='.0f', tickMinStep=1000)),
            y=alt.Y("count()", 
                   title="Number of Students",
                   axis=alt.Axis(tickMinStep=1)),
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)
    st.subheader("📈 Summary Stats")
    st.write(f"Average WTP: ₹{df['price'].mean():,.0f}")
    st.write(f"Median WTP: ₹{df['price'].median():,.0f}")
    st.write(f"Most Common WTP: ₹{df['price'].mode()[0]:,.0f}")
elif submitted:
    # This case: user submitted, but maybe it hasn't propagated yet
    st.info("Fetching data...")
else:
    # First-time visitors see this
    st.info("Waiting for the first submission...")
