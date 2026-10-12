import ccxt
import time
from typing import List, Any

class ExchangeClient:
        def __init__(self, config: dict):
                exch_cfg = config["exchange"]
                self.name = exch_cfg["name"]
                self.testnet = exch_cfg.get("testnet", False)

                exchange_class = getattr(ccxt, self.name)
                self.client = exchange_class({
                        "apiKey": exch_cfg["apiKey"],
                        "secret": exch_cfg["secret"],
                        "password": exch_cfg.get("password"),
                        "enableRateLimit": True,
                })

                # Some exchanges like binance have a 'test' flag
                if self.name == "binance" and self.testnet:
                        self.client.set_sandbox_mode(True)

        def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 200) -> List[List[Any]]:
                """Return OHLCV candles: [timestamp, open, high, low, close, volume]"""
                return self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

        def get_balance(self):
                return self.client.fetch_balance()

        def create_market_order(self, symbol: str, side: str, amount: float):
                """Place a market order if not in dry-run mode."""
                return self.client.create_order(symbol, "market", side, amount)

        def create_stop_loss_take_profit(self, symbol: str, side: str,
                                                                         amount: float, sl_price: float, tp_price: float):
                """
                Very exchange-specific in reality. Here we'll just return a dict,
                and you can later adapt for your exchange (OCO orders, etc.).
                """
                return {
                        "symbol": symbol,
                        "side": side,
                        "amount": amount,
                        "stop_loss": sl_price,
                        "take_profit": tp_price,
                        "note": "Implement with real conditional orders for your exchange."
                }

        def wait_for_rate_limit(self):
                # Simple throttle
                time.sleep(self.client.rateLimit / 1000.0)