import streamlit as st
import streamlit_functions as sql  # Import your SQL functions file

# Streamlit App Title
st.title("M&A Analysis Dashboard")
st.write("Welcome to the M&A Analysis Streamlit App for DA Ironhack 2025.")

# Ensure sql_functions has a `main()` function before running it
if hasattr(sql, 'main'):
    sql.main()
else:
    st.write("No main function found in streamlit_functions.py.")
