import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

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
3. Min ₹1,000 to Max ₹1,50,000  
4. If you enter any value greater than ₹1,50,000, it will be considered as ₹1,50,000  
""")

# --- Input Section ---
price = st.number_input("Enter your price (₹)", min_value=1000, max_value=150000, step=1000)
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
    
    # Count occurrences of each price
    price_counts = df['price'].value_counts().reset_index()
    price_counts.columns = ['price', 'count']
    
    # Sort by price in descending order
    price_counts = price_counts.sort_values('price', ascending=False)
    
    # Calculate cumulative sum of counts
    price_counts['cumulative_count'] = price_counts['count'].cumsum()
    
    # Create step chart with Plotly
    fig = px.line(
        price_counts,
        x='cumulative_count',
        y='price',
        title='Cumulative Demand Curve',
        labels={'cumulative_count': 'Cumulative Number of Students', 'price': 'Price (₹)'}
    )
    
    # Update to step line and static knee point labels
    fig.update_traces(
        mode='lines+markers+text',
        line_shape='hv',
        text=price_counts.apply(lambda row: f"({int(row['cumulative_count'])}, ₹{int(row['price']):,})", axis=1),
        textposition='top center',
        textfont=dict(size=10),
        marker=dict(size=8),
        hoverinfo='skip'  # Disable hovering
    )

    # Customize x-axis
    max_count = int(price_counts['cumulative_count'].max())
    fig.update_xaxes(
        range=[0, max_count + 0.5],
        tickmode='array',
        tickvals=list(range(0, max_count + 1)),
        ticktext=list(range(0, max_count + 1)),
        tickformat='.0f'
    )
    
    # Customize y-axis
    fig.update_yaxes(
        tick0=50000,
        dtick=10000,
        tickformat=',.0f'
    )
    
    # Final layout adjustments
    fig.update_layout(
        height=400,
        hovermode=False  # Completely disable hover mode
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary stats
    st.subheader("📈 Summary Stats")
    st.write(f"Average WTP: ₹{df['price'].mean():,.0f}")
    st.write(f"Median WTP: ₹{df['price'].median():,.0f}")
    st.write(f"Most Common WTP: ₹{df['price'].mode()[0]:,.0f}")
    
elif submitted:
    st.info("Fetching data...")
else:
    st.info("Waiting for the first submission...")
