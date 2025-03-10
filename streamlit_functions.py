import pandas as pd
import numpy as np
import pymysql
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text
import getpass  # To get the password without showing the input
import streamlit as st
import os  # Use environment variables instead of getpass


company_colors = {
    "Berkshire Hathaway": "#4B0082",
    "BlackRock":          "#000000",
    "Goldman Sachs":      "#A7E1FF",
    "JPMorgan Chase":     "#B5B5AC",
    "State Street":       "#003865"
}

# Mapping symbols to company names
symbol_to_company = {
    "BRK-B": "Berkshire Hathaway",
    "BLK": "BlackRock",
    "GS": "Goldman Sachs",
    "JPM": "JPMorgan Chase",
    "STT": "State Street"
}

#Set Streamlit dark mode background
DARK_BG = "#0E1117"
WHITE_TEXT = "white"

#Set up connection and password for SQL
def sql_setup():
    # Get database configuration from st.secrets
    db_config = st.secrets["database"]
    connection_string = (
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    )
    engine = create_engine(connection_string)
    return engine


# Total acquisitions per company
def total_acquisitions_by_company(engine):
    query = """
        SELECT acquirer, COUNT(*) AS total_acquisitions
        FROM mergers_acquisitions
        GROUP BY acquirer
        ORDER BY total_acquisitions DESC
    """
    df = pd.read_sql(query, engine)
    colors = [company_colors[acquirer] for acquirer in df['acquirer']]

    fig, ax = plt.subplots(figsize=(14, 8), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    df.plot(kind='bar', x='acquirer', y='total_acquisitions', color=colors, ax=ax)
    
    plt.xlabel('Acquirer', color=WHITE_TEXT)
    plt.ylabel('Total Acquisitions', color=WHITE_TEXT)
    plt.xticks(rotation=45, color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)
    plt.title('Total Acquisitions per Company', color=WHITE_TEXT)

    st.pyplot(fig)
    return df

# Acquisitions per year with acquirers included
def acquisitions_per_year(engine):
    query = """
        SELECT acquisition_year, acquirer, COUNT(*) AS total_acquisitions
        FROM mergers_acquisitions
        GROUP BY acquisition_year, acquirer
        ORDER BY acquisition_year DESC, total_acquisitions DESC
    """
    df = pd.read_sql(query, engine)
    pivot_df = df.pivot(index='acquisition_year', columns='acquirer', values='total_acquisitions').fillna(0)

    acquirer_colors = [company_colors[acquirer] for acquirer in pivot_df.columns]

    fig, ax = plt.subplots(figsize=(16, 9), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    pivot_df.plot(kind='bar', stacked=False, width=0.8, color=acquirer_colors, ax=ax)

    plt.xlabel('Year', color=WHITE_TEXT)
    plt.ylabel('Total Acquisitions', color=WHITE_TEXT)
    plt.title('Acquisitions per Year by Acquirer', color=WHITE_TEXT)
    plt.xticks(rotation=45, color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    st.pyplot(fig)
    return df


# Most active acquirer (top 1)
def most_active_acquirer(engine):
    query = """
        SELECT acquirer, COUNT(*) AS total_acquisitions
        FROM mergers_acquisitions
        GROUP BY acquirer
        ORDER BY total_acquisitions DESC
        LIMIT 1
    """
    df = pd.read_sql(query, engine)
    
    # Display in Streamlit
    st.subheader("Most Active Acquirer")
    st.dataframe(df) #works for streamlit
    
    return df

# Largest acquisition details
def largest_acquisition(engine):
    query = """
        SELECT acquired_company, acquirer, acquisition_price_usd, acquisition_date
        FROM mergers_acquisitions
        ORDER BY acquisition_price_usd DESC
        LIMIT 1
    """
    df = pd.read_sql(query, engine)

    df["acquisition_price_usd"] = df["acquisition_price_usd"] / 1e9
    df["acquisition_price_usd"] = df["acquisition_price_usd"].apply(lambda x: f"${x:,.2f}B")

    # Display in Streamlit
    st.subheader("Largest Acquisition Details")
    st.dataframe(df)  # works for streamlit
    
    return df

#Acquirer by maturity status (10+years means matured)
def maturity_status(engine):
    query = """
        SELECT acquirer, 
               CASE 
                   WHEN (YEAR(acquisition_date) - founded_year) >= 10 THEN 'Matured' 
                   ELSE 'Not Matured' 
               END AS matured
        FROM mergers_acquisitions
    """
    df = pd.read_sql(query, engine)
    maturity_counts = df.groupby(["acquirer", "matured"]).size().unstack()

    fig, ax = plt.subplots(figsize=(14, 8), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    maturity_counts.plot(kind="bar", stacked=True, colormap="tab10", ax=ax)

    plt.xlabel("Acquirer", color=WHITE_TEXT)
    plt.ylabel("Number of Acquisitions", color=WHITE_TEXT)
    plt.title("Preference for Matured vs. Non-Matured Companies by Acquirer", color=WHITE_TEXT)
    plt.xticks(rotation=45, color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)
    plt.legend(["Not Matured (<10 years)", "Matured (10+ years)"], title="Company Age at Acquisition", facecolor=DARK_BG, labelcolor=WHITE_TEXT)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    st.pyplot(fig)
    return df

#Industry distribution by Acquirer
def industry_distribution(engine):
    query = """
        SELECT acquirer, industry
        FROM mergers_acquisitions
    """
    df = pd.read_sql(query, engine)

    for acquirer in df["acquirer"].unique():
        plt.figure(figsize=(12, 7), facecolor=DARK_BG)
        df_subset = df[df["acquirer"] == acquirer]
        industry_counts = df_subset["industry"].value_counts()

        color = company_colors[acquirer]
        industry_counts.plot(kind="bar", color=color, alpha=0.75)

        plt.title(f"Industry Distribution for {acquirer}", color=WHITE_TEXT)
        plt.xlabel("Industry", color=WHITE_TEXT)
        plt.ylabel("Number of Acquisitions", color=WHITE_TEXT)
        plt.xticks(rotation=45, ha="right", color=WHITE_TEXT)
        plt.yticks(color=WHITE_TEXT)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        st.pyplot(plt.gcf())
        
    return df  


#Most expensive acquisitions by acquirer
def top_acquisitions(engine):
    query = """
        SELECT acquirer, acquired_company, acquisition_price_usd, acquisition_year
        FROM mergers_acquisitions
    """
    df = pd.read_sql(query, engine)
    df["acquisition_price_usd_billions"] = df["acquisition_price_usd"] / 1e9

    acquirer_table = df.groupby(['acquirer', 'acquired_company', 'acquisition_year'], as_index=False)['acquisition_price_usd_billions'].sum()
    top_acquisitions_per_acquirer = acquirer_table.groupby("acquirer").apply(lambda x: x.nlargest(3, "acquisition_price_usd_billions")).reset_index(drop=True)

    acquirer_colors = [company_colors[acquirer] for acquirer in top_acquisitions_per_acquirer["acquirer"]]

    fig, ax = plt.subplots(figsize=(18, 9), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    sns.barplot(data=top_acquisitions_per_acquirer, x="acquisition_price_usd_billions", y="acquired_company", hue="acquirer", palette=acquirer_colors, ax=ax)

    plt.xticks(rotation=45, ha="right", color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)
    plt.xlabel("Acquisition Price (in Billion USD)", color=WHITE_TEXT)
    plt.ylabel("Acquired Company", color=WHITE_TEXT)
    plt.title("Top 3 Acquisitions by Acquirer", color=WHITE_TEXT)

    for p in ax.patches:
        width = p.get_width()  
        if width > 0:  
            ax.annotate(f"${width:,.2f}B", (p.get_x() + width + 0.2, p.get_y() + p.get_height() / 2), ha='left', va='center', fontsize=9, fontweight='bold', color=WHITE_TEXT)

    plt.legend(title="Acquirer", bbox_to_anchor=(1, 1), loc="upper left", labelcolor=WHITE_TEXT, facecolor=DARK_BG)

    st.pyplot(fig)


#Acquisition prices in usd by acquirer
def acquisition_price_by_acquirer(engine):
    query = """
        SELECT acquirer, SUM(acquisition_price_usd) as total_acquisition_price_usd
        FROM mergers_acquisitions
        GROUP BY acquirer
    """
    df = pd.read_sql(query, engine)
    df["total_acquisition_price_usd"] /= 1e9

    colors = [company_colors[acquirer] for acquirer in df['acquirer']]

    fig, ax = plt.subplots(figsize=(14, 8), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    sns.barplot(x="acquirer", y="total_acquisition_price_usd", data=df, palette=colors, ax=ax)

    plt.xlabel("Acquirer", color=WHITE_TEXT)
    plt.ylabel("Acquisition Price (in Billion USD)", color=WHITE_TEXT)
    plt.title("Acquisition Price by Acquirer", color=WHITE_TEXT)
    plt.xticks(rotation=45, color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)

    st.pyplot(fig)

#Net income vs number of acquisitions
def net_income_vs_acquisitions(engine):
    query_ma = """
        SELECT c.symbol, COUNT(*) as num_acquisitions
        FROM mergers_acquisitions ma
        JOIN companies c ON ma.acquirer = c.company_name
        GROUP BY c.symbol
    """
    query_income = """
        SELECT symbol, statement_date AS date, netIncome
        FROM income_statements
    """
    df_ma = pd.read_sql(query_ma, engine)
    df_income = pd.read_sql(query_income, engine)

    df_income["date"] = pd.to_datetime(df_income["date"])
    df_income_latest = df_income.sort_values(by="date", ascending=False).drop_duplicates(subset=["symbol"])

    df_merged = pd.merge(df_income_latest, df_ma, on="symbol", how="left").fillna(0)
    df_merged["netIncome_billion"] = df_merged["netIncome"] / 1e9

    fig, ax = plt.subplots(figsize=(14, 8), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    palette = {sym: company_colors[symbol_to_company[sym]] for sym in df_merged["symbol"].unique()}
    sns.scatterplot(data=df_merged, x="netIncome_billion", y="num_acquisitions", hue="symbol", style="symbol", palette=palette, s=150, ax=ax)

    plt.xscale("log")
    plt.xlabel("Net Income (in Billions USD, Log Scale)", color=WHITE_TEXT)
    plt.ylabel("Number of M&A Deals", color=WHITE_TEXT)
    plt.title("Net Income vs. Number of Acquisitions by Acquirer", color=WHITE_TEXT)
    plt.xticks(color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)
    plt.legend(title="Company", bbox_to_anchor=(1, 1), facecolor=DARK_BG, labelcolor=WHITE_TEXT)

    st.pyplot(fig)
    return df

#Average pricing by maturity status
def avg_price_by_maturity(engine):
    query = """
        SELECT matured, AVG(acquisition_price_usd) as avg_acquisition_price_usd
        FROM mergers_acquisitions
        GROUP BY matured
    """
    df = pd.read_sql(query, engine)
    df["avg_acquisition_price_usd"] = df["avg_acquisition_price_usd"] / 1e9

    fig, ax = plt.subplots(figsize=(12, 7), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    sns.barplot(x=df["matured"].astype(str), y=df["avg_acquisition_price_usd"], palette="coolwarm", ax=ax)

    plt.xlabel("Maturity Status (0 = Non-Matured, 1 = Matured)", color=WHITE_TEXT)
    plt.ylabel("Average Acquisition Price (in Billions USD)", color=WHITE_TEXT)
    plt.title("Are Matured Companies More Expensive?", color=WHITE_TEXT)
    plt.xticks([0, 1], ["Not Matured (<10 years)", "Matured (10+ years)"], color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)

    st.pyplot(fig)
    return df

#M&A spending as a percentage of revenue
def ma_spending_vs_revenue(engine):
    query_ma = """
        SELECT c.symbol, YEAR(ma.acquisition_date) as year, SUM(ma.acquisition_price_usd) as total_ma_spending
        FROM mergers_acquisitions ma
        JOIN companies c ON ma.acquirer = c.company_name
        WHERE YEAR(ma.acquisition_date) >= 2020
        GROUP BY c.symbol, year
    """
    query_income = """
        SELECT symbol, YEAR(statement_date) as year, AVG(revenue) as avg_revenue
        FROM income_statements
        GROUP BY symbol, year
    """
    df_ma = pd.read_sql(query_ma, engine)
    df_income = pd.read_sql(query_income, engine)

    df_ma["total_ma_spending"] /= 1e9
    df_income["avg_revenue"] /= 1e9

    df_analysis = pd.merge(df_ma, df_income, on=["symbol", "year"], how="left")
    df_analysis["ma_spending_to_revenue"] = df_analysis["total_ma_spending"] / df_analysis["avg_revenue"]

    fig, ax = plt.subplots(figsize=(14, 8), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    for symbol in df_analysis["symbol"].unique():
        subset = df_analysis[df_analysis["symbol"] == symbol]
        company = symbol_to_company[symbol]
        plt.plot(subset["year"], subset["ma_spending_to_revenue"], marker="o", label=symbol, color=company_colors[company])

    plt.xlabel("Year", color=WHITE_TEXT)
    plt.ylabel("M&A Spending / Revenue Ratio", color=WHITE_TEXT)
    plt.title("M&A Spending Relative to Revenue by Acquirer (Since 2020)", color=WHITE_TEXT)
    plt.xticks(color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)
    plt.legend(title="Acquirer", bbox_to_anchor=(1.05, 1), loc="upper left", facecolor=DARK_BG, labelcolor=WHITE_TEXT)
    plt.grid(True)

    st.pyplot(fig)
    return df


#Stock price comparison as of last time data was pulled
def stock_price_comparison(engine):
    query = """
        SELECT symbol, AVG(price) as avg_price, MAX(stock_timestamp) as last_update
        FROM stock_prices
        GROUP BY symbol
    """
    df = pd.read_sql(query, engine)
    last_update = df["last_update"].max()

    colors = [company_colors[symbol_to_company[symbol]] for symbol in df['symbol']]

    fig, ax = plt.subplots(figsize=(14, 8), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    sns.barplot(data=df, x="symbol", y="avg_price", palette=colors, ax=ax)

    for p in ax.patches:
        ax.annotate(f"${p.get_height():,.2f}", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom', fontsize=10, color=WHITE_TEXT)

    plt.xlabel("Company", color=WHITE_TEXT)
    plt.ylabel("Stock Price (USD)", color=WHITE_TEXT)
    plt.title(f"Stock Price Comparison of Acquiring Companies (As of {last_update})", color=WHITE_TEXT)
    plt.xticks(rotation=45, color=WHITE_TEXT)
    plt.yticks(color=WHITE_TEXT)

    st.pyplot(fig)
    return df


#Run any of the above analysis function.
def run_analysis(engine):
    while True:
        print("\nChoose an analysis to run:")
        print("1: Total Acquisitions by Company")
        print("2: Acquisitions per Year")
        print("3: Most Active Acquirer")
        print("4: Largest Acquisition")
        print("5: Matured (+10 years) vs Not Matured  (<10 years)")
        print("6: Industry Distribution by Company")
        print("7: Top 3 Acquisitions by Company")
        print("8: Acquisition Price by Acquirer")
        print("9: Net Income vs Number of Acquisitions")
        print("10: Average Acquisition Price by Maturity Status")
        print("11: M&A Spending relative to Revenue by Acquirer (Since 2020)")
        print("12: Stock Price Comparison of Acquiring Companies")
        print("Type Exit, to end the program")

        choice = input("Enter your choice (1-12): ")

        if choice == '1':
            total_acquisitions_by_company(engine)
        elif choice == '2':
            acquisitions_per_year(engine)
        elif choice == '3':
            most_active_acquirer(engine)
        elif choice == '4':
            largest_acquisition(engine)
        elif choice == '5':
            maturity_status(engine)
        elif choice == '6':
            industry_distribution(engine)
        elif choice == '7':
            top_acquisitions(engine)
        elif choice == '8':
            acquisition_price_by_acquirer(engine)
        elif choice == '9':
            net_income_vs_acquisitions(engine)
        elif choice == '10':
            avg_price_by_maturity(engine)
        elif choice == '11':
            ma_spending_vs_revenue(engine)
        elif choice == '12':
            stock_price_comparison(engine)
        elif choice.strip().lower() == 'exit':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

def insert_data(engine):
    """
    Allows user to insert data into one of the database tables interactively in Streamlit.
    """
    st.subheader("Insert Data into Database")

    # Fetch available tables dynamically
    query_tables = "SHOW TABLES"
    tables_df = pd.read_sql(query_tables, engine)

    if tables_df.empty:
        st.error("No tables found in the database.")
        return

    # Select table with Streamlit dropdown
    table_name = st.selectbox("Select the table to insert data:", tables_df.iloc[:, 0])

    if not table_name:
        return

    # Get table schema
    query = f"DESCRIBE {table_name}"
    df_schema = pd.read_sql(query, engine)

    # Collect user inputs for each column
    st.subheader(f"Enter Data for `{table_name}`")
    data = {}

    for index, row in df_schema.iterrows():
        column_name = row["Field"]
        column_type = row["Type"]

        # Skip auto-increment primary key columns
        if "auto_increment" in row["Extra"]:
            continue

        # Use Streamlit inputs based on column type
        if "int" in column_type or "bigint" in column_type:
            data[column_name] = st.number_input(f"{column_name} ({column_type})", step=1, format="%d")
        elif "float" in column_type or "decimal" in column_type:
            data[column_name] = st.number_input(f"{column_name} ({column_type})", format="%.2f")
        elif "date" in column_type.lower():
            data[column_name] = st.text_input(f"{column_name} (YYYY-MM-DD)")
        elif "bool" in column_type or column_type.lower() == "tinyint(1)":
            data[column_name] = st.checkbox(f"{column_name} (Check = True, Uncheck = False)")
        else:
            data[column_name] = st.text_input(f"{column_name}")

    # Insert Data Button
    if st.button(f"Insert Data into `{table_name}`"):
        try:
            # Create SQL INSERT statement
            columns = ", ".join(data.keys())
            values_placeholders = ", ".join([f":{col}" for col in data.keys()])
            sql = text(f"INSERT INTO {table_name} ({columns}) VALUES ({values_placeholders})")

            # Execute insertion
            with engine.connect() as conn:
                conn.execute(sql, data)
                conn.commit()

            st.success(f"Data successfully inserted into `{table_name}`!")
        except Exception as e:
            st.error(f"Error inserting data: {e}")


def delete_entry(engine):
    """
    Allows user to delete an entry from a selected table based on 'symbol' or 'company_name' in Streamlit.
    """
    st.subheader("Delete Data from Database")

    # Fetch available tables dynamically
    query_tables = "SHOW TABLES"
    tables_df = pd.read_sql(query_tables, engine)

    if tables_df.empty:
        st.error("No tables found in the database.")
        return

    # Select table from dropdown
    table_name = st.selectbox("Select the table to delete data from:", tables_df.iloc[:, 0])

    if not table_name:
        return

    query = f"DESCRIBE {table_name}"
    df_schema = pd.read_sql(query, engine)
    valid_columns = [col for col in ["symbol", "company_name"] if col.lower() in map(str.lower, df_schema["Field"].values)]

    if not valid_columns:
        st.error(f"The table `{table_name}` does not have 'symbol' or 'company_name'. Deletion is not allowed.")
        return

    # Select column name dynamically
    column_name = st.selectbox("Select the column to filter by:", valid_columns)

    # Enter the value to delete
    value = st.text_input(f"Enter the value for `{column_name}` (e.g., 'AAPL' or 'Apple Inc.'):")

    # Confirm deletion with a button
    if st.button(f"Delete Entries from `{table_name}`"):
        if not value:
            st.warning("Please enter a value to delete.")
            return

        # Prepare and execute the DELETE statement
        sql = text(f"DELETE FROM {table_name} WHERE LOWER({column_name}) = LOWER(:value)")
        params = {'value': value}

        try:
            with engine.connect() as conn:
                result = conn.execute(sql, params)
                conn.commit()
            
            if result.rowcount > 0:
                st.success(f"{result.rowcount} record(s) deleted from `{table_name}` where `{column_name}` = '{value}'.")
            else:
                st.warning(f"No records found matching `{column_name}` = '{value}'.")
        except Exception as e:
            st.error(f"Error deleting data: {e}")


def main():
    print("sql_functions.py loaded. Use this in a script or application.")

if __name__ == "__main__":
    main()
