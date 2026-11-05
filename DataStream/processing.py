import numpy as np
import pandas as pd 

def calculate_volatility(data: pd.DataFrame) -> float:
    #Exctract closing prices
    prices = data["Close"].dropna()

    if len(prices) < 3:
        raise ValueError("Insufficient price history")

    if (prices <= 0).any():
        raise ValueError("Closing prices must be positive")

    # Calculate daily Logarithmic returns
    log_returns = np.log(prices / prices.shift(1)).dropna()

    # Annualized historical volatility
    volatility = log_returns.std(ddof=1) * np.sqrt(252)

    return float(volatility)



if __name__ == "__main__":
    from ingestion import fetch_market_data

    data = fetch_market_data("AAPL")

    volatility = calculate_volatility(data)
    print(f"AAPL annualized volatility: {volatility:.2%}")