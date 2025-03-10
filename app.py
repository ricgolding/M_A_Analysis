import streamlit as st
import streamlit_functions as sql  # Import the SQL functions

# Streamlit App Title
st.title("M&A Analysis Dashboard")
st.write("Welcome to the M&A Analysis Streamlit App for DA Ironhack 2025.")

# Create a sidebar menu
option = st.sidebar.selectbox(
    "Choose an action:",
    ("Run Data Analysis", "Insert Data", "Delete Entry")
)

# Setup database connection
engine = sql.sql_setup()

# Handle user selections
if option == "Run Data Analysis":
    st.subheader("Choose an analysis function:")
    analysis_functions = {
        "Total Acquisitions by Company": sql.total_acquisitions_by_company,
        "Acquisitions per Year": sql.acquisitions_per_year,
        "Most Active Acquirer": sql.most_active_acquirer,
        "Largest Acquisition": sql.largest_acquisition,
        "Maturity Status": sql.maturity_status,
        "Industry Distribution": sql.industry_distribution,
        "Top Acquisitions": sql.top_acquisitions,
        "Acquisition Price by Acquirer": sql.acquisition_price_by_acquirer,
        "Net Income vs Acquisitions": sql.net_income_vs_acquisitions,
        "M&A Spending vs Revenue": sql.ma_spending_vs_revenue,
        "Stock Price Comparison": sql.stock_price_comparison
    }

    selected_analysis = st.selectbox("Select an analysis:", list(analysis_functions.keys()))
    
    if st.button("Run Analysis"):
        analysis_functions[selected_analysis](engine)

elif option == "Insert Data":
    st.subheader("Insert Data")
    sql.insert_data(engine)

elif option == "Delete Entry":
    st.subheader("Delete Data")
    sql.delete_entry(engine)
