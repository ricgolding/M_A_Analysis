import pandas as pd
import numpy as np
import pymysql
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text
import getpass  # To get the password without showing the input

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

#Set up connection and password for SQL
def sql_setup():
    password = getpass.getpass("Please add your SQL password: ")
    bd = "mergers_acquisitions"
    connection_string = 'mysql+pymysql://root:' + password + '@localhost/'+bd
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

    #list to map company colors
    colors = [company_colors[acquirer] for acquirer in df['acquirer']]
    ax = df.plot(kind='bar', 
                 x='acquirer', 
                 y='total_acquisitions', 
                 color=colors, 
                 figsize=(10,6), 
                 title='Total Acquisitions per Company',
                legend=False)
    
    plt.xlabel('Acquirer')
    plt.ylabel('Total Acquisitions')
    plt.xticks(rotation=45)
    plt.show()
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

    colors = [company_colors[acquirer] for acquirer in pivot_df.columns]
    
    ax = pivot_df.plot(kind='bar', stacked=False, figsize=(14, 7), width=0.8, color=colors)

    plt.title('Acquisitions per Year by Acquirer')
    plt.xlabel('Year')
    plt.ylabel('Total Acquisitions')
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()
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
    display(df)
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

    display(df)
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

    # Group by acquirer and maturity status, then count occurrences
    maturity_counts = df.groupby(["acquirer", "matured"]).size().unstack()

    # Create a stacked bar chart
    maturity_counts.plot(kind="bar", stacked=True, figsize=(12, 6), colormap="tab10")

    # Add labels and title
    plt.xlabel("Acquirer")
    plt.ylabel("Number of Acquisitions")
    plt.title("Preference for Matured vs. Non-Matured Companies by Acquirer")
    plt.legend(["Not Matured (<10 years)", "Matured (10+ years)"], title="Company Age at Acquisition")

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Show plot
    plt.show()

    return df  

#Industry distribution by Acquirer
def industry_distribution(engine):
    query = """
        SELECT acquirer, industry
        FROM mergers_acquisitions
    """
    df = pd.read_sql(query, engine)

    for acquirer in df["acquirer"].unique():
        plt.figure(figsize=(10, 6))
        df_subset = df[df["acquirer"] == acquirer]
        industry_counts = df_subset["industry"].value_counts()
        
        industry_counts.plot(kind="bar", color=company_colors[acquirer], alpha=0.75)

        plt.title(f"Industry Distribution of Acquisitions for {acquirer}")
        plt.xlabel("Industry")
        plt.ylabel("Number of Acquisitions")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()
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
    
    top_acquisitions_per_acquirer = acquirer_table.groupby("acquirer").apply(
        lambda x: x.nlargest(3, "acquisition_price_usd_billions")).reset_index(drop=True)

    plt.figure(figsize=(14, 7))
    ax = sns.barplot(data=top_acquisitions_per_acquirer, 
                     x="acquisition_price_usd_billions", 
                     y="acquired_company", 
                     hue="acquirer", 
                     palette=company_colors)

    plt.xticks(rotation=45, ha="right")
    plt.title("Top 3 Acquisitions by Acquirer")
    plt.xlabel("Acquisition Price (in Billion USD)")
    plt.ylabel("Acquired Company")

    for p, (_, row) in zip(ax.patches, top_acquisitions_per_acquirer.iterrows()):
        width = p.get_width()
        if width > 0:
            ax.annotate(f"${width:,.2f}B",  
                        (p.get_x() + width + 0.2, p.get_y() + p.get_height() / 2),  
                        ha='left', va='center', fontsize=9, fontweight='bold', color='black')

    plt.legend(title="Acquirer", bbox_to_anchor=(1, 1))
    plt.show()
    return df 

#Acquisition prices in usd by acquirer
def acquisition_price_by_acquirer(engine):
    query = """
        SELECT acquirer, SUM(acquisition_price_usd) as total_acquisition_price_usd
        FROM mergers_acquisitions
        GROUP BY acquirer
    """
    df = pd.read_sql(query, engine)
    df["total_acquisition_price_usd"] = df["total_acquisition_price_usd"] / 1e9

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x="acquirer", y="total_acquisition_price_usd", data=df, palette=company_colors)

    plt.title("Acquisition Price by Acquirer")
    plt.xlabel("Acquirer")
    plt.ylabel("Acquisition Price (in Billion USD)")
    plt.xticks(rotation=45)
    plt.show()
    return df

#Net income vs number of acquisitions
def net_income_vs_acquisitions(engine):
    query_ma = """
        SELECT c.symbol, COUNT(*) as num_acquisitions
        FROM mergers_acquisitions ma
        JOIN companies c ON ma.acquirer = c.company_name
        WHERE c.symbol IS NOT NULL
        GROUP BY c.symbol
    """
    
    query_income = """
        SELECT symbol, statement_date AS date, netIncome
        FROM income_statements
    """
    
    df_ma = pd.read_sql(query_ma, engine)
    df_income = pd.read_sql(query_income, engine)

    # Process data
    df_income["date"] = pd.to_datetime(df_income["date"])
    df_income_latest = df_income.sort_values(by="date", ascending=False).drop_duplicates(subset=["symbol"])
    
    # Merge datasets
    df_merged = pd.merge(df_income_latest, df_ma, on="symbol", how="outer").fillna(0)
    df_merged["netIncome_billion"] = np.log1p(df_merged["netIncome"] / 1e9)  # Log transform

    company_colors = {
        "BRK-B": "#4B0082",
        "BLK": "#000000",
        "GS": "#A7E1FF",
        "JPM": "#B5B5AC",
        "STT": "#003865"
    }
    
    # Plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df_merged, 
        x="netIncome_billion", 
        y="num_acquisitions", 
        hue="symbol",  
        style="symbol",  
        palette=company_colors,  
        s=150  
    )
    plt.title("Net Income vs. Number of Acquisitions by Acquirer")
    plt.xlabel("Log(1 + Net Income in Billions USD)")
    plt.ylabel("Number of M&A Deals")
    plt.xticks(rotation=45)
    plt.legend(title="Company", bbox_to_anchor=(1, 1))  
    plt.show()


#Average pricing by maturity status
def avg_price_by_maturity(engine):
    query = """
        SELECT matured, AVG(acquisition_price_usd) as avg_acquisition_price_usd
        FROM mergers_acquisitions
        GROUP BY matured
    """
    df = pd.read_sql(query, engine)

    # Convert to billions
    df["avg_acquisition_price_usd"] = df["avg_acquisition_price_usd"] / 1e9

    plt.figure(figsize=(8, 5))
    sns.barplot(x=df["matured"].astype(str), y=df["avg_acquisition_price_usd"], palette="coolwarm")
    plt.xlabel("Maturity Status (0 = Non-Matured, 1 = Matured)")
    plt.ylabel("Average Acquisition Price (in Billions USD)")
    plt.title("Are Matured Companies More Expensive?")
    plt.xticks([0, 1], ["Not Matured (<10 years)", "Matured (10+ years)"])
    plt.show()

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

    # Convert to billions
    df_ma["total_ma_spending"] = df_ma["total_ma_spending"] / 1e9
    df_income["avg_revenue"] = df_income["avg_revenue"] / 1e9

    # Merge data
    df_analysis = pd.merge(df_ma, df_income, on=["symbol", "year"], how="left")
    df_analysis["ma_spending_to_revenue"] = df_analysis["total_ma_spending"] / df_analysis["avg_revenue"]

    plt.figure(figsize=(12, 6))
    for symbol in df_analysis["symbol"].unique():
        subset = df_analysis[df_analysis["symbol"] == symbol]
        company_name = symbol_to_company[symbol]
        plt.plot(subset["year"], subset["ma_spending_to_revenue"], 
                 marker="o", label=symbol, color=company_colors[company_name])

    plt.title("M&A Spending Relative to Revenue by Acquirer (Since 2020)")
    plt.xlabel("Year")
    plt.ylabel("M&A Spending / Revenue Ratio")
    plt.legend(title="Acquirer", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True)
    plt.show()


#Stock price comparison as of last time data was pulled
def stock_price_comparison(engine):
    """
    Plots a stock price comparison of acquiring companies, displaying the latest stock_timestamp in the title.
    """
    query = """
        SELECT symbol, AVG(price) as avg_price, MAX(stock_timestamp) as last_update
        FROM stock_prices
        GROUP BY symbol
    """
    df = pd.read_sql(query, engine)

    # Get the latest timestamp
    last_update = df["last_update"].max()

    # Map symbols to colors
    colors = [company_colors[symbol_to_company[symbol]] for symbol in df['symbol']]

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df, x="symbol", y="avg_price", palette=colors)

    # Add value labels
    for p in ax.patches:
        ax.annotate(f"${p.get_height():,.2f}", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='bottom', fontsize=10, color='black')

    plt.title(f"Stock Price Comparison of Acquiring Companies (As of {last_update})")
    plt.xlabel("Company")
    plt.ylabel("Stock Price (USD)")
    plt.xticks(rotation=45)
    plt.show()



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
    Allows user to insert data into one of the database tables interactively.
    """
    # Fetch available tables dynamically
    query_tables = "SHOW TABLES"
    tables_df = pd.read_sql(query_tables, engine)
    tables = {str(i+1): table for i, table in enumerate(tables_df.iloc[:, 0])}  # Fixed empty dictionary issue

    if not tables:
        print("No tables found in the database.")
        return

    # Display available tables
    print("Select the table you want to insert data into:")
    for key, value in tables.items():
        print(f"{key}. {value}")

    choice = input("Enter the number of the table: ").strip()

    if choice not in tables:
        print("Invalid choice. Please try again.")
        return
    
    table_name = tables[choice]

    # Get table schema
    query = f"DESCRIBE {table_name}"
    df_schema = pd.read_sql(query, engine)

    # Prompt user for input based on table schema
    data = {}
    print(f"\nEntering data for table: {table_name}")

    for index, row in df_schema.iterrows():
        column_name = row["Field"]
        column_type = row["Type"]
        
        # Skip auto-increment primary key columns
        if "auto_increment" in row["Extra"]:
            continue

        while True:
            user_input = input(f"Enter value for {column_name} ({column_type}): ").strip()

            try:
                # Convert input to correct type
                if "int" in column_type or "bigint" in column_type:
                    data[column_name] = int(user_input)
                elif "float" in column_type or "decimal" in column_type:
                    data[column_name] = float(user_input)
                elif "date" in column_type.lower():
                    data[column_name] = user_input  # Ensure input follows YYYY-MM-DD format
                elif "bool" in column_type or column_type.lower() == "tinyint(1)":
                    data[column_name] = 1 if user_input.lower() in ["1", "true", "yes"] else 0
                else:
                    data[column_name] = user_input  # Default to string
                break  # Exit loop if input is valid
            except ValueError:
                print(f"Invalid input format for {column_name}. Expected {column_type}. Please try again.")

    # Confirm deletion
    confirm = input(f"\n Are you sure you want to insert these entries? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Deletion cancelled.")
        return
    
    # Create SQL INSERT statement
    columns = ", ".join(data.keys())
    values_placeholders = ", ".join([f":{col}" for col in data.keys()])
    sql = text(f"INSERT INTO {table_name} ({columns}) VALUES ({values_placeholders})")

    # Execute insertion
    try:
        with engine.connect() as conn:
            conn.execute(sql, data)
            conn.commit()
        print(f"\n Data successfully inserted into `{table_name}`!")
    except Exception as e:
        print(f"\n Error inserting data: {e}")

def delete_entry(engine):
    """
    Allows user to delete an entry from a selected table based on 'symbol' or 'company_name'.
    """
    # Fetch available tables dynamically
    query_tables = "SHOW TABLES"
    tables_df = pd.read_sql(query_tables, engine)
    tables = {str(i+1): table for i, table in enumerate(tables_df.iloc[:, 0])}

    if not tables:
        print("No tables found in the database.")
        return

    # Display available tables
    print("\nSelect the table you want to delete data from:")
    for key, value in tables.items():
        print(f"{key}. {value}")

    choice = input("\nEnter the number of the table: ").strip()
    
    if choice not in tables:
        print("Invalid choice. Please try again.")
        return
    
    table_name = tables[choice]

    # Ensure the selected table has either 'symbol' or 'company_name'
    query = f"DESCRIBE {table_name}"
    df_schema = pd.read_sql(query, engine)
    valid_columns = [col for col in ["symbol", "company_name"] if col.lower() in map(str.lower, df_schema["Field"].values)]

    if not valid_columns:
        print(f"\nThe table `{table_name}` does not have 'symbol' or 'company_name'. Deletion is not allowed.")
        return

    # Ask user for the identifier
    print("\nYou can delete by either 'symbol' or 'company_name'.")
    
    while True:
        column_name = input(f"Enter 'symbol' or 'company_name' to filter by: ").strip()
        if column_name.lower() in map(str.lower, valid_columns):
            # Get the correct case from the database
            column_name = next(col for col in valid_columns if col.lower() == column_name.lower())
            break
        print("Invalid choice. Please enter either 'symbol' or 'company_name'.")

    # Ask for the value to match
    value = input(f"Enter the value for `{column_name}` (e.g., 'AAPL' or 'Apple Inc.'): ").strip()

    # Confirm deletion
    confirm = input(f"\nAre you sure you want to delete entries where `{column_name}` = '{value}' in `{table_name}`? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Deletion cancelled.")
        return

    # Prepare and execute the DELETE statement
    sql = text(f"DELETE FROM {table_name} WHERE LOWER({column_name}) = LOWER(:value)")
    params = {'value': value}

    try:
        with engine.connect() as conn:
            result = conn.execute(sql, params)
            conn.commit()
        print(f"\n{result.rowcount} record(s) deleted from `{table_name}` where `{column_name}` = '{value}'.")
    except Exception as e:
        print(f"\nError deleting data: {e}")
