from collections import defaultdict
from datetime import datetime
import numpy as np

def compute_gex(options):
    gex_by_strike = defaultdict(lambda: {"call": 0.0, "put": 0.0})
    for opt in options:
        strike = opt["strike"]
        gamma = opt["gamma"]
        oi = opt["open_interest"]
        gex = gamma * oi * 100
        if opt["option_type"] == "call":
            gex_by_strike[strike]["call"] += gex
        elif opt["option_type"] == "put":
            gex_by_strike[strike]["put"] += gex

    result = []
    zero_gamma_strike = None
    min_diff = float("inf")
    call_wall = (0, 0)
    put_wall = (0, 0)

    for strike, gex_values in sorted(gex_by_strike.items()):
        net_gex = gex_values["call"] + gex_values["put"]
        result.append({
            "strike": strike,
            "call_gex": gex_values["call"],
            "put_gex": gex_values["put"],
            "net_gex": net_gex
        })
        if abs(net_gex) < min_diff:
            zero_gamma_strike = strike
            min_diff = abs(net_gex)
        if gex_values["call"] > call_wall[1]:
            call_wall = (strike, gex_values["call"])
        if gex_values["put"] < put_wall[1]:
            put_wall = (strike, gex_values["put"])

    return {
        "data": result,
        "zero_gamma": zero_gamma_strike,
        "call_wall": call_wall[0],
        "put_wall": put_wall[0]
    }

def calculate_gex_details(option_book, spot_price):
    """
    从完整的期权数据中计算GEX详情。
    """
    # 1. 找到最近的交易日
    if not option_book:
        return { "data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": None }

    expirations = sorted(list(set(inst.get("expiration_timestamp") for inst in option_book)))
    if not expirations:
        return { "data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": None }

    closest_expiration_ts = expirations[0]
    closest_expiration_date = datetime.utcfromtimestamp(closest_expiration_ts / 1000).date()

    # 2. 按行权价汇总GEX
    gex_by_strike = {}

    for inst in option_book:
        if inst.get("expiration_timestamp") != closest_expiration_ts:
            continue

        gamma = inst.get("greeks", {}).get("gamma", 0)
        oi = inst.get("open_interest", 0)
        strike = inst["strike"]
        
        if strike not in gex_by_strike:
            gex_by_strike[strike] = {"call_gex": 0, "put_gex": 0}

        gex_value = gamma * oi * (spot_price**2) * 0.01 / 1_000_000  # in millions USD

        if inst["option_type"] == "call":
            gex_by_strike[strike]["call_gex"] += gex_value
        else:
            gex_by_strike[strike]["put_gex"] += -gex_value # Put GEX is negative

    if not gex_by_strike:
        return { "data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": closest_expiration_date.strftime('%Y-%m-%d') }

    # 3. 格式化数据并计算指标
    strikes = sorted(gex_by_strike.keys())
    data = [{"strike": s, "call_gex": gex_by_strike[s]["call_gex"], "put_gex": gex_by_strike[s]["put_gex"]} for s in strikes]
    
    net_gex_by_strike = np.array([d["call_gex"] + d["put_gex"] for d in data])
    strike_array = np.array(strikes)
    
    # 4. 重新计算 Zero Gamma (使用插值)
    zero_gamma = None
    try:
        # 寻找net_gex穿过0的索引
        sign_change = np.where(np.diff(np.sign(net_gex_by_strike)))[0]
        if len(sign_change) > 0:
            # 取最接近现货价格的那个翻转点
            closest_flip_idx = sign_change[np.argmin(np.abs(strike_array[sign_change] - spot_price))]
            x1, x2 = strike_array[closest_flip_idx], strike_array[closest_flip_idx + 1]
            y1, y2 = net_gex_by_strike[closest_flip_idx], net_gex_by_strike[closest_flip_idx + 1]
            # 线性插值找到y=0时的x
            zero_gamma = x1 - y1 * (x2 - x1) / (y2 - y1)
    except Exception as e:
        print(f"Could not calculate zero gamma: {e}")

    # 5. 计算其他指标
    total_call_gex = sum(d["call_gex"] for d in data)
    total_put_gex = sum(d["put_gex"] for d in data) # this will be negative
    net_gex = total_call_gex + total_put_gex
    call_wall = max(data, key=lambda x: x["call_gex"])["strike"] if data else None
    put_wall = min(data, key=lambda x: x["put_gex"])["strike"] if data else None

    return {
        "data": data,
        "spot_price": spot_price,
        "zero_gamma": float(zero_gamma) if zero_gamma is not None else None,
        "call_wall": float(call_wall) if call_wall is not None else None,
        "put_wall": float(put_wall) if put_wall is not None else None,
        "expiration_date": closest_expiration_date.strftime('%Y-%m-%d'),
        "total_call_gex": total_call_gex,
        "total_put_gex": total_put_gex,
        "net_gex": net_gex,
        "last_update_time": datetime.utcnow().isoformat() + "Z"
    }
