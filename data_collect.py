import yaml
import pandas as pd
from pathlib import Path
from exchange_client import ExchangeClient

def load_config(path: str = "config.yaml") -> dict:
        with open(path, "r") as f:
                return yaml.safe_load(f)

def ohlcv_to_df(ohlcv):
        cols = ["timestamp", "open", "high", "low", "close", "volume"]
        df = pd.DataFrame(ohlcv, columns=cols)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

def main():
        config = load_config()
        trading_cfg = config["trading"]
        symbol = trading_cfg["symbol"]
        timeframe = trading_cfg["timeframe"]

        exchange = ExchangeClient(config)

        # Fetch up to 1000 candles (most exchanges limit this)
        limit = 1000
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = ohlcv_to_df(ohlcv)

        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        filename_symbol = symbol.replace("/", "")
        filepath = data_dir / f"ohlcv_{filename_symbol}_{timeframe}.csv"

        df.to_csv(filepath, index=False)
        print(f"Saved {len(df)} candles to {filepath}")

if __name__ == "__main__":
        main()