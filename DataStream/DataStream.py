import math

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ingestion import fetch_market_data
from processing import calculate_volatility

app = FastAPI(
    title="DataStream API",
    description="Financial Market Data Pipeline",
    version="0.3.0"
)

class MarketData(BaseModel):
    symbol: str
    spot: float = Field(gt=0)
    historical_volatility: float = Field(ge=0)
    currency: str
    observation_date: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "DataStream",
        "version": "0.3.0"
    }

@app.get("/market-data/{symbol}", response_model=MarketData)
def get_market_data(symbol: str):
    symbol = symbol.strip().upper()

    if not symbol or len(symbol) > 20:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid symbol"
        )
    try:
        # Retrieve historical volatility
        data = fetch_market_data(symbol)

        # Calculate historical volatility
        volatility = calculate_volatility(data)

        # Latest available closing price
        spot = float(data["Close"].dropna().iloc[-1])

        if not math.isfinite(spot) or spot <= 0:
            raise ValueError("Invalid latest closing price")

        if not math.isfinite(volatility):
            raise ValueError("Invalid volatility")

        # Yahoo Finance historical prices are indexed by data
        observation_date = data.index[-1].date().isoformat()

        # Currency metadata supplied by yfinance
        currency = data.attrs.get("currency", "UNKNOWN")

        return MarketData(
            symbol=symbol,
            spot=spot,
            historical_volatility=volatility,
            currency=currency,
            observation_date=observation_date
        )
    
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc



    