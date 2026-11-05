import yfinance as yf
import pandas as pd 

def fetch_market_data(symbol: str) -> pd.DataFrame:
    ticker = yf.Ticker(symbol)

    data = ticker.history(period="1y")

    if data.empty:
        raise ValueError(
            f"No market data found for {symbol}"
        )

    return data

if __name__ == "__main__":
    data = fetch_market_data("AAPL")
    print(data.head())
