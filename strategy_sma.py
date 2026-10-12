import pandas as pd

class SMACrossoverStrategy:
        def __init__(self, fast_window: int = 10, slow_window: int = 30):
                self.fast_window = fast_window
                self.slow_window = slow_window
                self.position = 0    # -1 short, 0 flat, 1 long

        def generate_signal(self, ohlcv_df: pd.DataFrame) -> int:
                """
                Returns:
                        1    -> signal to go long
                        -1 -> signal to go short
                         0 -> hold / no change
                """
                if len(ohlcv_df)  < self.slow_window:
                        return 0

                close = ohlcv_df["close"]
                fast_ma = close.rolling(self.fast_window).mean()
                slow_ma = close.rolling(self.slow_window).mean()

                if fast_ma.iloc[-1] > slow_ma.iloc[-1] and self.position  <= 0:
                        # Bullish crossover (go long)
                        self.position = 1
                        return 1
                elif fast_ma.iloc[-1]  < slow_ma.iloc[-1] and self.position >= 0:
                        # Bearish crossover (go short)
                        self.position = -1
                        return -1
                else:
                        # No change in position
                        return 0