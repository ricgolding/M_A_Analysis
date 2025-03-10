import pandas as pd
import requests
from datetime import datetime

# FinancialModelingPrepAPI API

class FinancialModelingPrepAPI:
    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key):
        self.api_key = api_key

    def _get(self, endpoint, params=None):
        """Helper method to send GET requests to the API."""
        if params is None:
            params = {}
        params["apikey"] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        print(f"Fetching data from: {url}")
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_income_statement(self, ticker, limit=5):
        """
        Fetches the income statement for a given company.
        
        :param ticker: str - Stock ticker symbol (e.g., "BLK" for BlackRock).
        :param limit: int - Number of years to fetch.
        :return: DataFrame of income statements.
        """
        endpoint = f"income-statement/{ticker}?limit={limit}"
        data = self._get(endpoint)
        return pd.DataFrame(data)


    def get_stock_quote(self, ticker):
        """
        Fetches the latest stock quote for a given company and adds a timestamp.
        
        :param ticker: str - Stock ticker symbol.
        :return: Dictionary with stock price details and timestamp.
        """
        endpoint = f"quote/{ticker}"
        data = self._get(endpoint)
    
        if data:
            stock_data = data[0]
            stock_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add timestamp
            return stock_data
        return None

    def get_company_profile(self, ticker):
        """
        Fetches company profile, including industry & sector classification.
        
        :param ticker: str - Stock ticker symbol.
        :return: Dictionary with company profile.
        """
        endpoint = f"profile/{ticker}"
        data = self._get(endpoint)
        return data[0] if data else None 


# Initialize API key
api_key = "KgyAuneVfEujskT2xrOVEH1yjE3VZ2t1"
fmp = FinancialModelingPrepAPI(api_key)


# Function to safely convert data to DataFrame
def safe_df_conversion(data):
    return pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame()