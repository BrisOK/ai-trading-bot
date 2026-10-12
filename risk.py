from typing import Tuple

def compute_position_size(price: float, config: dict) -> float:
        """
        Compute position size in units of the base asset, given:
        - max_position_usd
        - risk_per_trade (fraction of max_position_usd)
        """
        trading_cfg = config["trading"]
        max_usd = trading_cfg["max_position_usd"]
        risk_frac = trading_cfg["risk_per_trade"]

        usd_risk = max_usd * risk_frac
        # Amount of asset to buy, roughly (ignores fees/slippage)
        amount = usd_risk / price
        return amount

def compute_sl_tp(price: float, side: str, config: dict) -> Tuple[float, float]:
        """
        Return (stop_loss_price, take_profit_price).
        side: "buy" (long) or "sell" (short).
        """
        trading_cfg = config["trading"]
        sl_pct = trading_cfg["sl_pct"]
        tp_pct = trading_cfg["tp_pct"]

        if side == "buy":
                sl_price = price * (1 - sl_pct)
                tp_price = price * (1 + tp_pct)
        else:    # short
                sl_price = price * (1 + sl_pct)
                tp_price = price * (1 - tp_pct)

        return sl_price, tp_price