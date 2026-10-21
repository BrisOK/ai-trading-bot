import yaml
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

def load_config(path: str = "config.yaml") -> dict:
        with open(path, "r") as f:
                return yaml.safe_load(f)

def build_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Build simple features from OHLCV.
        We only use 'close' for now.
        """
        df = df.copy()
        df["return_1"] = df["close"].pct_change(1)
        df["return_3"] = df["close"].pct_change(3)
        df["return_6"] = df["close"].pct_change(6)

        df["ma_5"] = df["close"].rolling(5).mean()
        df["ma_10"] = df["close"].rolling(10).mean()
        df["ma_20"] = df["close"].rolling(20).mean()

        df["vol_5"] = df["return_1"].rolling(5).std()
        df["vol_10"] = df["return_1"].rolling(10).std()

        # Future 3-candle return as target
        df["future_return_3"] = df["close"].shift(-3) / df["close"] - 1.0

        # Target: 1 if price goes up over next 3 candles, else 0
        df["target"] = (df["future_return_3"] > 0).astype(int)

        # Drop rows with NaNs
        df = df.dropna().reset_index(drop=True)
        return df

def main():
        config = load_config()
        trading_cfg = config["trading"]
        strat_cfg = config["strategy"]

        symbol = trading_cfg["symbol"]
        timeframe = trading_cfg["timeframe"]

        filename_symbol = symbol.replace("/", "")
        data_path = Path("data") / f"ohlcv_{filename_symbol}_{timeframe}.csv"
        if not data_path.exists():
                raise FileNotFoundError(
                        f"{data_path} not found. Run data_collect.py first."
                )

        df = pd.read_csv(data_path, parse_dates=["timestamp"])
        df = build_features(df)

        feature_cols = [
                "return_1", "return_3", "return_6",
                "ma_5", "ma_10", "ma_20",
                "vol_5", "vol_10",
        ]

        X = df[feature_cols].values
        y = df["target"].values

        X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
        )

        model = RandomForestClassifier(
                n_estimators=200,
                max_depth=5,
                random_state=42,
                n_jobs=-1,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {acc:.4f}")
        print(classification_report(y_test, y_pred))

        # Save model + feature metadata
        model_package = {
                "model": model,
                "feature_cols": feature_cols,
        }

        model_path = Path(strat_cfg["model_path"])
        model_path.parent.mkdir(exist_ok=True, parents=True)
        joblib.dump(model_package, model_path)
        print(f"Saved model to {model_path}")

if __name__ == "__main__":
        main()