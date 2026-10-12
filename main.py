import time
import yaml
import pandas as pd
from pathlib import Path

from exchange_client import ExchangeClient
from strategy_sma import SMACrossoverStrategy
from risk import compute_position_size, compute_sl_tp
from utils import setup_logger

logger = setup_logger("ai_trading_bot")

def load_config(path: str = "config.yaml") -> dict:
        with open(path, "r") as f:
                return yaml.safe_load(f)

def ohlcv_to_df(ohlcv) -> pd.DataFrame:
        cols = ["timestamp", "open", "high", "low", "close", "volume"]
        df = pd.DataFrame(ohlcv, columns=cols)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

def main():
        if not Path("config.yaml").exists():
                raise FileNotFoundError(
                        "config.yaml not found. Copy config.example.yaml to config.yaml and set your API keys."
                )

        config = load_config()
        exch_cfg = config["trading"]
        symbol = exch_cfg["symbol"]
        timeframe = exch_cfg["timeframe"]
        max_candles = config["runtime"]["max_candles"]
        interval = config["runtime"]["poll_interval_sec"]
        dry_run = config["runtime"]["dry_run"]

        exchange = ExchangeClient(config)

        strat_cfg = config["strategy"]
        strategy = SMACrossoverStrategy(
                fast_window=strat_cfg["fast_window"],
                slow_window=strat_cfg["slow_window"],
        )

        logger.info(f"Starting bot on {symbol} ({timeframe}) dry_run={dry_run}")

        # Initial data
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=max_candles)
        df = ohlcv_to_df(ohlcv)

        while True:
                try:
                        # Fetch latest candles
                        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=max_candles)
                        df = ohlcv_to_df(ohlcv)

                        # Generate signal
                        signal = strategy.generate_signal(df)
                        last_close = df["close"].iloc[-1]

                        if signal == 1:
                                side = "buy"
                                logger.info(f"Long signal at price {last_close}")
                        elif signal == -1:
                                side = "sell"
                                logger.info(f"Short signal at price {last_close}")
                        else:
                                logger.info("No new signal.")
                                time.sleep(interval)
                                continue

                        # Compute size & SL/TP
                        amount = compute_position_size(last_close, config)
                        sl_price, tp_price = compute_sl_tp(last_close, side, config)
                        logger.info(f"Amount: {amount:.6f} | SL: {sl_price:.2f} | TP: {tp_price:.2f}")

                        if dry_run:
                                logger.info("[DRY RUN] Would place market order + SL/TP here.")
                        else:
                                # Live order placement
                                order = exchange.create_market_order(symbol, side, amount)
                                logger.info(f"Market order placed: {order}")
                                stp = exchange.create_stop_loss_take_profit(symbol, side, amount, sl_price, tp_price)
                                logger.info(f"SL/TP (pseudo): {stp}")

                        time.sleep(interval)

                except KeyboardInterrupt:
                        logger.info("Bot stopped by user.")
                        break
                except Exception as e:
                        logger.exception(f"Error in main loop: {e}")
                        time.sleep(5)

if __name__ == "__main__":
        main()