import requests
from collections import defaultdict
import numpy as np
from datetime import datetime

DERIBIT_BASE = "https://www.deribit.com/api/v2"

def fetch_spot_price(currency: str):
    """获取标的资产的实时现货价格"""
    # Deribit使用永续合约价格作为指数参考
    instrument_name = f"{currency}-PERPETUAL"
    response = requests.get(f"{DERIBIT_BASE}/public/ticker", params={"instrument_name": instrument_name})
    data = response.json()
    if "result" in data and "mark_price" in data["result"]:
        return data["result"]["mark_price"]
    else:
        raise Exception(f"Could not fetch spot price for {currency}")

def fetch_instruments(currency: str):
    """获取所有可用的期权合约"""
    response = requests.get(f"{DERIBIT_BASE}/public/get_instruments", params={
        "currency": currency,
        "kind": "option",
        "expired": "false"  # API expects a string, not a boolean
    })
    data = response.json()
    if "result" in data:
        return data["result"]
    else:
        # 如果API返回错误，抛出异常
        raise Exception(f"Deribit API error on get_instruments: {data.get('error')}")

def fetch_greeks(instrument_name: str):
    """获取某个合约的 Greeks"""
    response = requests.get(f"{DERIBIT_BASE}/public/ticker", params={"instrument_name": instrument_name})
    data = response.json()
    if "result" in data:
        return data["result"]
    else:
        # 忽略单个合约的错误，而不是让整个应用失败
        print(f"Warning: Could not fetch greeks for {instrument_name}. Error: {data.get('error')}")
        return None

def get_gex_data(currency: str = "BTC"):
    # 1. 获取所有期权和实时现货价
    instruments = fetch_instruments(currency)
    spot_price = fetch_spot_price(currency)
    
    # 获取今天的UTC日期以筛选当日到期 (0DTE) 的合约
    today_utc = datetime.utcnow().date()
    
    gex_by_strike = defaultdict(lambda: {"call_gex": 0, "put_gex": 0})

    for inst in instruments:
        try:
            # 筛选当日到期的合约
            expiration_timestamp = inst.get("expiration_timestamp")
            if expiration_timestamp:
                expiration_date = datetime.utcfromtimestamp(expiration_timestamp / 1000).date()
                if expiration_date != today_utc:
                    continue  # 如果不是今天到期，则跳过
            else:
                continue # 如果没有时间戳，跳过

            greeks = fetch_greeks(inst["instrument_name"])
            if greeks is None:  # 如果获取greeks失败则跳过
                continue

            gamma = greeks.get("greeks", {}).get("gamma", 0)
            oi = greeks.get("open_interest", 0) # Open Interest in contracts
            strike = inst["strike"]
            is_call = inst["option_type"] == "call"

            # 2. 应用GEX计算公式 (Gamma * OI * (Spot Price)^2 * 0.01)
            # 结果以百万美元为单位，方便图表显示
            gex_value = gamma * oi * (spot_price**2) * 0.01 / 1_000_000

            if is_call:
                gex_by_strike[strike]["call_gex"] += gex_value
            else:
                gex_by_strike[strike]["put_gex"] += -gex_value  # Put GEX 记为负值

        except Exception as e:
            print(f"Error processing instrument {inst.get('instrument_name', 'N/A')}: {e}")
            continue

    if not gex_by_strike:
        return { "data": [], "zero_gamma": None, "call_wall": None, "put_wall": None }

    # 3. 汇总数据并排序
    strikes = sorted(gex_by_strike.keys())
    data = [{"strike": s, "call_gex": gex_by_strike[s]["call_gex"], "put_gex": gex_by_strike[s]["put_gex"]} for s in strikes]

    # 4. 计算 Zero Gamma, Call Wall, Put Wall
    total_gamma_by_strike = np.array([d["call_gex"] + d["put_gex"] for d in data])
    strike_array = np.array([d["strike"] for d in data])
    
    zero_gamma = None
    # 寻找累积Gamma最接近0的点
    cumulative_gamma = np.cumsum(total_gamma_by_strike)
    zero_gamma_idx = np.argmin(np.abs(cumulative_gamma))
    if zero_gamma_idx < len(strike_array):
        zero_gamma = strike_array[zero_gamma_idx]

    # Call Wall: 正GEX最高的执行价
    call_wall = max(data, key=lambda x: x["call_gex"])["strike"]
    # Put Wall: 负GEX最低的执行价 (绝对值最大)
    put_wall = min(data, key=lambda x: x["put_gex"])["strike"]

    return {
        "data": data,
        "zero_gamma": float(zero_gamma) if zero_gamma is not None else None,
        "call_wall": float(call_wall) if call_wall is not None else None,
        "put_wall": float(put_wall) if put_wall is not None else None
    }
