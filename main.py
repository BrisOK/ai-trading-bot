from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models, schemas, crud
from ai_model import get_signal_for_symbol
import yfinance as yf
import requests

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Trading API", version="0.2.0")

# CORS stays the same
origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)


@app.get("/health")
def health_check():
        return {"status": "ok"}


@app.get("/trades", response_model=list[schemas.Trade])
def list_trades(db: Session = Depends(get_db)):
        return crud.get_trades(db)


@app.post("/trades", response_model=schemas.Trade)
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
        if trade.side not in ["buy", "sell"]:
                raise HTTPException(status_code=400, detail="side must be 'buy' or 'sell'")
        return crud.create_trade(db, trade)


@app.get("/signals", response_model=list[schemas.Signal])
def list_signals(symbol: str | None = None, db: Session = Depends(get_db)):
        return crud.get_signals(db, symbol)


@app.post("/signals", response_model=schemas.Signal)
def generate_signal(payload: schemas.SignalRequest, db: Session = Depends(get_db)):
        market = payload.market.lower()
        if market not in ("stock", "crypto"):
                raise HTTPException(status_code=400, detail="market must be 'stock' or 'crypto'")

        prediction, recommendation = get_signal_for_symbol(payload.symbol, market=market)
        signal = crud.create_signal(db, payload.symbol.upper(), prediction, recommendation)
        return signal


@app.get("/price")
def get_price(symbol: str, market: str = "stock"):
        """
        Get latest price for a symbol, for display in the UI.

        - stock: uses Yahoo Finance
        - crypto: uses Binance public API
        """
        try:
                symbol_up = symbol.upper()
                if market == "crypto":
                        # Binance ticker price endpoint
                        url = "https://api.binance.com/api/v3/ticker/price"
                        resp = requests.get(url, params={"symbol": symbol_up}, timeout=10)
                        resp.raise_for_status()
                        data = resp.json()
                        price = float(data["price"])
                else:
                        # Stock price via yfinance
                        ticker = yf.Ticker(symbol_up)
                        hist = ticker.history(period="1d")
                        if hist.empty:
                                raise ValueError(f"No price data for stock symbol {symbol_up}")
                        price = float(hist["Close"].iloc[-1])

                return {
                        "symbol": symbol_up,
                        "market": market,
                        "price": price,
                }
        except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))