import streamlit as st
import streamlit_functions as sql  # Import the SQL functions

#Streamlit page settings (MUST be the first command)
st.set_page_config(page_title="M&A Analysis", layout="wide")

# Streamlit App Title
st.title("M&A Analysis Dashboard")
st.write("Welcome to the M&A Analysis Streamlit App for DA Ironhack 2025.")

# Company logos
company_logos = {
    "Berkshire Hathaway": "berkshire.png",
    "BlackRock": "blackrock.jpg",
    "Goldman Sachs": "goldman.png",
    "JPMorgan Chase": "jpmorgan.png",
    "State Street": "statestreet.png"
}

# Display logos in a row
st.markdown("### **Companies in this Analysis**")

col1, col2, col3, col4, col5 = st.columns(5)  # Creates 5 equal columns

with col1:
    st.image(company_logos["Berkshire Hathaway"], caption="Berkshire Hathaway", use_column_width=True)

with col2:
    st.image(company_logos["BlackRock"], caption="BlackRock", use_column_width=True)

with col3:
    st.image(company_logos["Goldman Sachs"], caption="Goldman Sachs", use_column_width=True)

with col4:
    st.image(company_logos["JPMorgan Chase"], caption="JPMorgan Chase", use_column_width=True)

with col5:
    st.image(company_logos["State Street"], caption="State Street", use_column_width=True)

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
