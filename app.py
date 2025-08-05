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
    st.subheader("📊 Cumulative Demand Curve")
    
    # Process data for cumulative demand
    price_counts = df['price'].value_counts().reset_index()
    price_counts.columns = ['price', 'count']
    
    # Sort by price in descending order
    price_counts = price_counts.sort_values('price', ascending=False)
    
    # Calculate cumulative sum of counts
    price_counts['cumulative_count'] = price_counts['count'].cumsum()
    
    # Create step chart
    chart = (
        alt.Chart(price_counts)
        .mark_line(interpolate='step-after')
        .encode(
            x=alt.X('cumulative_count:Q', 
                    title='Cumulative Number of Students',
                    axis=alt.Axis(tickMinStep=1, format='d')),
            y=alt.Y('price:Q', 
                    title='Price (₹)',
                    axis=alt.Axis(format='.0f', tickMinStep=1000)),
            tooltip=[
                alt.Tooltip('price:Q', title='Price', format='₹,.0f'),
                alt.Tooltip('count:Q', title='Students at this price'),
                alt.Tooltip('cumulative_count:Q', title='Total students')
            ]
        )
        .properties(height=400)
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    st.subheader("📈 Summary Stats")
    st.write(f"Average WTP: ₹{df['price'].mean():,.0f}")
    st.write(f"Median WTP: ₹{df['price'].median():,.0f}")
    st.write(f"Most Common WTP: ₹{df['price'].mode()[0]:,.0f}")
    
    st.subheader("📊 Price and Cumulative Table")
    
    # Create display table with formatted price
    display_table = price_counts.copy()
    display_table['Price (₹)'] = display_table['price'].apply(lambda x: f"₹{x:,}")
    display_table['Students at this Price'] = display_table['count']
    display_table['Cumulative Students'] = display_table['cumulative_count']
    
    # Select and reorder columns for display
    final_table = display_table[['Price (₹)', 'Students at this Price', 'Cumulative Students']]
    
    st.dataframe(final_table, use_container_width=True, hide_index=True)

elif submitted:
    st.info("Fetching data...")
else:
    st.info("Waiting for the first submission...")
