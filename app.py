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
    # Count occurrences of each price
    price_counts = df['price'].value_counts().reset_index()
    price_counts.columns = ['price', 'count']
    # Sort by price in descending order
    price_counts = price_counts.sort_values('price', ascending=False)
    # Calculate cumulative sum of counts
    price_counts['cumulative_count'] = price_counts['count'].cumsum()
    
    # Calculate differences for annotations
    price_counts['price_diff'] = price_counts['price'].diff().fillna(0).abs()  # Absolute price difference
    price_counts['count_diff'] = price_counts['cumulative_count'].diff().fillna(0)  # Change in cumulative count
    
    # Create step chart with Plotly
    fig = px.line(
        price_counts,
        x='cumulative_count',
        y='price',
        title='Cumulative Demand Curve',
        labels={'cumulative_count': 'Cumulative Number of Students', 'price': 'Price (₹)'}
    )
    # Update to step line
    fig.update_traces(mode='lines', line_shape='hv')  # 'hv' creates a step-after effect
    
    # Add annotations for price difference and count change
    annotations = []
    for i in range(1, len(price_counts)):
        x0 = price_counts['cumulative_count'].iloc[i-1]
        x1 = price_counts['cumulative_count'].iloc[i]
        y0 = price_counts['price'].iloc[i-1]
        y1 = price_counts['price'].iloc[i]
        price_diff = price_counts['price_diff'].iloc[i]
        count_diff = price_counts['count_diff'].iloc[i]
        
        # Only add annotation if there's a change in count
        if count_diff > 0:
            # Position annotation at the midpoint of the step
            x_mid = (x0 + x1) / 2
            y_mid = y1  # Place at the lower price level of the step
            annotations.append(
                dict(
                    x=x_mid,
                    y=y_mid,
                    xref="x",
                    yref="y",
                    text=f"ΔP: ₹{int(price_diff):,}<br>ΔC: {int(count_diff)}",
                    showarrow=True,
                    arrowhead=2,
                    ax=20,  # Arrow x offset
                    ay=30,  # Arrow y offset
                    font=dict(size=10),
                    align="center",
                    bgcolor="rgba(255, 255, 255, 0.8)",  # Semi-transparent background
                    bordercolor="black",
                    borderwidth=1
                )
            )
    
    # Update layout with annotations
    fig.update_layout(annotations=annotations)
    
    # Customize x-axis to start at 0 and show every integer tick
    max_count = int(price_counts['cumulative_count'].max())  # Get max cumulative count as integer
    fig.update_xaxes(
        range=[0, max_count + 0.5],  # Extend range slightly to ensure last tick is visible
        tickmode='array',  # Use array mode to specify exact ticks
        tickvals=list(range(0, max_count + 1)),  # Show every integer from 0 to max_count
        ticktext=list(range(0, max_count + 1)),  # Display integers as tick labels
        tickformat='.0f'  # No decimals
    )
    # Customize y-axis
    fig.update_yaxes(
        tick0=50000,  # Start at min price
        dtick=10000,  # Steps of 10,000 for price
        tickformat=',.0f'  # No decimals, with comma for thousands
    )
    # Set chart height and make it responsive
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📈 Summary Stats")
    st.write(f"Average WTP: ₹{df['price'].mean():,.0f}")
    st.write(f"Median WTP: ₹{df['price'].median():,.0f}")
    st.write(f"Most Common WTP: ₹{df['price'].mode()[0]:,.0f}")
elif submitted:
    st.info("Fetching data...")
else:
    st.info("Waiting for the first submission...")
