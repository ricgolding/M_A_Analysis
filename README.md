# **Mergers & Acquisitions (M&A) Data Analysis Project**

## **Overview**
This project is a **comprehensive data analysis of Mergers & Acquisitions (M&A)**, covering the **entire data pipeline** from **data extraction and cleaning to exploratory analysis, statistical testing, and visualization**. The goal is to **analyze acquisition trends, financial behaviors, and industry patterns** using data from **Financial Modeling Prep API** and **Tracxn Excel datasets**.

Additionally, an **interactive dashboard was developed in Streamlit** to enable **data exploration and visualization**. Further, **Tableau visualizations** provide additional insights.

🔗 **Live Streamlit Dashboard**: [M&A Analysis Dashboard](https://m-a-analysis-app.streamlit.app/)  
📊 **Tableau Visualizations**: *(not available yet)*

---

## **Features**
### **Data Collection & Cleaning**
- Extracted financial and M&A data from **Financial Modeling Prep API** and **Tracxn**.
- Cleaned and formatted datasets using **Pandas**.
- Stored structured data in a **MySQL database**.

### **Exploratory Data Analysis (EDA) & Hypothesis Testing**
- Conducted **descriptive statistics** on M&A trends.
- Performed **hypothesis testing**, including:
  - **ANOVA on Acquisition Prices for Large Acquisitions**: Analyzing if acquisition prices differ significantly among acquirers.
  - **ANOVA on Acquisition Prices Across Acquirers in the Same Industry**.
  - **Chi² Test on BlackRock's Preference for Mature Companies**: Testing if BlackRock acquires companies older than 10+ years more frequently.
  - **Industry-Level T-Test on Acquisition Prices**: Comparing BlackRock and Berkshire Hathaway’s acquisition pricing within the same industry.
- Used **t-tests, ANOVA, and chi-square tests** for statistical validation.

### **Interactive Streamlit Dashboard**

#### 🛠 **User Interaction**
✅ **Run Analysis** - identifies acquisition trends and financial strategy via **MySQL**. 
✅ **Insert new M&A data** directly into MySQL via a **Streamlit form**.  
✅ **Delete existing M&A records** based on **company name or symbol**.   

### **Interactive Tableau Dashboard**
#### 📊 **M&A Visualizations & Insights** 

✅ **Acquisition Trends Dashboard** - interactive dashboard for deeper insights into KPIs.

---

## **Installation & Setup**
### **🔧 Prerequisites**
- Python 3.x
- MySQL database
- Streamlit, Pandas, SQLAlchemy, Matplotlib, Seaborn

### **📥 Clone the Repository**
```bash
git clone https://github.com/ricgolding/M_A_Analysis.git
```

### **📌 Install Dependencies**
```bash
pip install -r requirements.txt
```

### **🛠 Configure MySQL Connection**
Set up the database connection in **Streamlit secrets**:
1. Create a `.streamlit/secrets.toml` file.
2. Add your MySQL credentials:
```toml
[database]
user = "your_username"
password = "your_password"
host = "localhost"
port = 3306
name = "mergers_acquisitions"
```

### **🚀 Run the Streamlit App**
```bash
streamlit run app.py
```

---

## **Usage**
- **Visualize** M&A trends across companies and industries.
- **Analyze** financial relationships between acquisitions and revenue/net income.
- **Modify the database** by adding or removing data entries interactively.
- **Explore statistical findings** on M&A behaviors.
- **Use Tableau visualizations** for deeper insights.

---

## **Project Structure**
```
📂 M_A_Analysis
├── 📂 .streamlit
│   ├── secrets.toml  # MySQL credentials
├── 📂 data
│   ├── tracxn_mna.xlsx  # Raw dataset from Tracxn
├── 📂 notebooks
│   ├── data_cleaning.ipynb  # Cleaning & preprocessing
│   ├── eda.ipynb  # Exploratory Data Analysis
│   ├── statistical_testing.ipynb  # Hypothesis testing & statistical analysis
├── 📂 src
│   ├── streamlit_functions.py  # M&A analysis functions for Streamlit
│   ├── sql_setup.py  # Database connection setup
├── app.py  # Streamlit application entry point
├── requirements.txt  # Python dependencies
├── README.md  # Project documentation
```

---

## **Future Improvements**
- Automate data extraction & updates from APIs.
- Add real-time M&A tracking functionality.
- Expand dataset to include more financial metrics.
- Implement **predictive analytics** for M&A trend forecasting.
- Enhance **data visualization** with more interactive elements.

---

## **Author**
👤 **Ricardo Golding**  
📧 [goldingra@gmail.com](mailto:goldingra@gmail.com)  
🐙 [GitHub](https://github.com/ricgolding)  

---

🚀 *This project delivers data-driven insights into the M&A landscape, helping analyze corporate acquisition strategies and trends.*

