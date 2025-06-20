import requests
from collections import defaultdict
import numpy as np

DERIBIT_BASE = "https://www.deribit.com/api/v2"

def fetch_instruments(currency: str):
    """获取所有可用的期权合约"""
    response = requests.get(f"{DERIBIT_BASE}/public/get_instruments", params={
        "currency": currency,
        "kind": "option",
        "expired": "false"
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
    instruments = fetch_instruments(currency)
    gex_by_strike = defaultdict(lambda: {"call_gex": 0, "put_gex": 0})

    for inst in instruments:
        try:
            greeks = fetch_greeks(inst["instrument_name"])
            if greeks is None:  # 如果获取greeks失败则跳过
                continue

            gamma = greeks.get("greeks", {}).get("gamma", 0)
            size = greeks.get("open_interest", 0)
            strike = inst["strike"]
            is_call = inst["option_type"] == "call"

            gex_value = gamma * size * 100  # GEX 估算方法

            if is_call:
                gex_by_strike[strike]["call_gex"] += gex_value
            else:
                gex_by_strike[strike]["put_gex"] += -gex_value  # put gamma 记为负值

        except Exception as e:
            print(f"Error processing instrument {inst.get('instrument_name', 'N/A')}: {e}")
            continue

    # 汇总为列表并按 strike 排序
    strikes = sorted(gex_by_strike.keys())
    data = [{"strike": s, "call_gex": gex_by_strike[s]["call_gex"], "put_gex": gex_by_strike[s]["put_gex"]} for s in strikes]

    # 计算 zero gamma 点
    all_gamma = np.array([d["call_gex"] + d["put_gex"] for d in data])
    strike_array = np.array([d["strike"] for d in data])

    try:
        zero_gamma_idx = np.argmin(np.abs(np.cumsum(all_gamma)))
        zero_gamma = strike_array[zero_gamma_idx]
    except Exception:
        zero_gamma = None

    # Call Wall 和 Put Wall
    call_wall = max(data, key=lambda x: x["call_gex"])["strike"] if data else None
    put_wall = min(data, key=lambda x: x["put_gex"])["strike"] if data else None

    return {
        "data": data,
        "zero_gamma": zero_gamma,
        "call_wall": call_wall,
        "put_wall": put_wall
    }
