import pandas as pd
from strategy_sma import SMACrossoverStrategy
from risk import compute_position_size, compute_sl_tp

def backtest_sma(ohlcv_df: pd.DataFrame, config: dict) -> pd.DataFrame:
        """
        Simple backtest: enter/exit at close price of signals.
        """
        strat_cfg = config["strategy"]
        strategy = SMACrossoverStrategy(
                fast_window=strat_cfg["fast_window"],
                slow_window=strat_cfg["slow_window"],
        )

        ohlcv_df = ohlcv_df.copy()
        ohlcv_df["position"] = 0
        ohlcv_df["pnl"] = 0.0

        current_pos = 0
        entry_price = None

        for i in range(len(ohlcv_df)):
                sub_df = ohlcv_df.iloc[: i + 1]
                signal = strategy.generate_signal(sub_df)
                price = ohlcv_df.iloc[i]["close"]

                if signal == 1 and current_pos  <= 0:
                        # Close short if any, open long
                        if current_pos == -1 and entry_price is not None:
                                ohlcv_df.loc[ohlcv_df.index[i], "pnl"] += (entry_price - price)
                        current_pos = 1
                        entry_price = price

                elif signal == -1 and current_pos >= 0:
                        # Close long if any, open short
                        if current_pos == 1 and entry_price is not None:
                                ohlcv_df.loc[ohlcv_df.index[i], "pnl"] += (price - entry_price)
                        current_pos = -1
                        entry_price = price

                ohlcv_df.loc[ohlcv_df.index[i], "position"] = current_pos

        # Sum PnL; this is very naive (ignores fees/size)
        ohlcv_df["cum_pnl"] = ohlcv_df["pnl"].cumsum()
        return ohlcv_df