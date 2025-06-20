import requests
from collections import defaultdict
import numpy as np
from datetime import datetime, date
import concurrent.futures

DERIBIT_BASE = "https://www.deribit.com/api/v2"

def fetch_spot_price(currency: str):
    currency = currency.upper()
    if currency in ['BTC', 'ETH']:
        instrument_name = f"{currency}-PERPETUAL"
        response = requests.get(f"{DERIBIT_BASE}/public/ticker", params={"instrument_name": instrument_name})
        response.raise_for_status()
        data = response.json()
        if "result" in data and "mark_price" in data["result"]:
            return data["result"]["mark_price"]
        else:
            raise Exception(f"Could not fetch spot price for {currency}")
    elif currency in ['SOL', 'XRP']:
        index_name = f"{currency.lower()}_usd"
        response = requests.get(f"{DERIBIT_BASE}/public/get_index_price", params={"index_name": index_name})
        response.raise_for_status()
        data = response.json()
        if "result" in data and "index_price" in data["result"]:
            return data["result"]["index_price"]
        else:
            raise Exception(f"Could not fetch index price for {currency}")
    else:
        raise Exception(f"Spot price fetch not supported for {currency}")

def fetch_full_option_book(currency: str):
    """通过单个高效API调用获取全部期权数据"""
    response = requests.get(f"{DERIBIT_BASE}/public/get_book_summary_by_currency", params={
        "currency": currency,
        "kind": "option"
    })
    response.raise_for_status()
    data = response.json()
    if "result" in data:
        return data["result"]
    else:
        raise Exception(f"Deribit API error on get_book_summary_by_currency: {data.get('error')}")

def fetch_instruments(currency: str):
    """获取所有可用的期权合约"""
    response = requests.get(f"{DERIBIT_BASE}/public/get_instruments", params={
        "currency": currency.upper(),
        "kind": "option",
        "expired": "false"  # API expects a string, not a boolean
    })
    data = response.json()
    print(f"fetch_instruments({currency}) count: {len(data.get('result', []))}")
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
    print(f"{currency} instruments count: {len(instruments)}")
    for inst in instruments[:5]:
        print(f"Sample instrument: {inst}")
    spot_price = fetch_spot_price(currency)
    if not instruments:
        return { "data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": None }
    expirations = sorted(list(set(inst.get("expiration_timestamp") for inst in instruments)))
    if not expirations:
        return { "data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": None }
    closest_expiration_ts = expirations[0]
    closest_expiration_date = datetime.utcfromtimestamp(closest_expiration_ts / 1000).date()
    gex_by_strike = defaultdict(lambda: {"oi": {"call_gex": 0, "put_gex": 0}, "vol": {"call_gex": 0, "put_gex": 0}})
    # 用并发批量抓取greeks
    filtered_instruments = [inst for inst in instruments if inst.get("expiration_timestamp") == closest_expiration_ts]
    print(f"Filtered instruments for closest expiration: {len(filtered_instruments)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        greeks_results = list(executor.map(
            lambda inst: (inst, fetch_greeks(inst["instrument_name"])),
            filtered_instruments
        ))
    for inst, greeks in greeks_results[:5]:
        print(f"Sample greeks for {inst['instrument_name']}: {greeks}")
    for inst, greeks in greeks_results:
        try:
            if greeks is None:
                continue
            gamma = greeks.get("greeks", {}).get("gamma", 0)
            oi = greeks.get("open_interest", 0)
            volume = greeks.get("stats", {}).get("volume", 0)
            strike = inst["strike"]
            is_call = inst["option_type"] == "call"
            gex_by_oi_value = gamma * oi * (spot_price**2) * 0.01 / 1_000_000
            gex_by_volume_value = gamma * volume * (spot_price**2) * 0.01 / 1_000_000
            if is_call:
                gex_by_strike[strike]["oi"]["call_gex"] += gex_by_oi_value
                gex_by_strike[strike]["vol"]["call_gex"] += gex_by_volume_value
            else:
                gex_by_strike[strike]["oi"]["put_gex"] += -gex_by_oi_value
                gex_by_strike[strike]["vol"]["put_gex"] += -gex_by_volume_value
        except Exception as e:
            print(f"Error processing instrument {inst.get('instrument_name', 'N/A')}: {e}")
            continue

    if not gex_by_strike:
        return { "data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": closest_expiration_date.strftime('%Y-%m-%d') }

    # 4. 汇总数据并排序
    strikes = sorted(gex_by_strike.keys())
    # Chart data is based on Volume, as requested
    data = [{"strike": s, "call_gex": gex_by_strike[s]["vol"]["call_gex"], "put_gex": gex_by_strike[s]["vol"]["put_gex"]} for s in strikes]

    # 5. 计算指标 (基于持仓量 OI)
    total_oi_call_gex = sum(gex_by_strike[s]["oi"]["call_gex"] for s in strikes)
    total_oi_put_gex = sum(gex_by_strike[s]["oi"]["put_gex"] for s in strikes)
    net_oi_gex = total_oi_call_gex + total_oi_put_gex
    call_wall = max(data, key=lambda x: x["call_gex"]) if data else None
    if call_wall:
        call_wall = call_wall["strike"]
    put_wall_data = [d for d in data if d["put_gex"] != 0] # Filter out zero put gex
    put_wall = min(put_wall_data, key=lambda x: x["put_gex"])["strike"] if put_wall_data else None

    # 计算 Zero Gamma (基于持仓量 OI)
    total_gex_by_strike = np.array([d["call_gex"] + d["put_gex"] for d in data])
    strike_array = np.array([d["strike"] for d in data])
    zero_gamma = None
    try:
        sign_change_indices = np.where(np.diff(np.sign(total_gex_by_strike)))[0]
        if len(sign_change_indices) > 0:
            closest_flip_idx = sign_change_indices[np.argmin(np.abs(strike_array[sign_change_indices] - spot_price))]
            x1, x2 = strike_array[closest_flip_idx], strike_array[closest_flip_idx + 1]
            y1, y2 = total_gex_by_strike[closest_flip_idx], total_gex_by_strike[closest_flip_idx + 1]
            if (y2 - y1) != 0:
                zero_gamma = x1 - y1 * (x2 - x1) / (y2 - y1)
    except Exception:
        pass # Zero gamma calculation can fail, it's not critical
    
    # 6. 计算交易量指标 (GEX by Volume)
    vol_data = [{"strike": s, "call_gex": gex_by_strike[s]["vol"]["call_gex"], "put_gex": gex_by_strike[s]["vol"]["put_gex"]} for s in strikes]
    total_vol_call_gex = sum(d["call_gex"] for d in vol_data)
    total_vol_put_gex = sum(d["put_gex"] for d in vol_data)
    net_vol_gex = total_vol_call_gex + total_vol_put_gex
    total_vol_gex_by_strike = np.array([d["call_gex"] + d["put_gex"] for d in vol_data])
    zero_gamma_vol = None
    try:
        sign_change_indices_vol = np.where(np.diff(np.sign(total_vol_gex_by_strike)))[0]
        if len(sign_change_indices_vol) > 0:
            closest_flip_idx_vol = sign_change_indices_vol[np.argmin(np.abs(strike_array[sign_change_indices_vol] - spot_price))]
            x1_vol, x2_vol = strike_array[closest_flip_idx_vol], strike_array[closest_flip_idx_vol + 1]
            y1_vol, y2_vol = total_vol_gex_by_strike[closest_flip_idx_vol], total_vol_gex_by_strike[closest_flip_idx_vol + 1]
            if (y2_vol - y1_vol) != 0:
                zero_gamma_vol = x1_vol - y1_vol * (x2_vol - x1_vol) / (y2_vol - y1_vol)
    except Exception:
        pass

    return {
        "data": data,
        "expiration_date": closest_expiration_date.strftime('%Y-%m-%d'),
        
        # GEX by Open Interest
        "zero_gamma": float(zero_gamma) if zero_gamma is not None else None,
        "call_wall": float(call_wall) if call_wall is not None else None,
        "put_wall": float(put_wall) if put_wall is not None else None,
        "total_oi_call_gex": total_oi_call_gex,
        "total_oi_put_gex": total_oi_put_gex,
        "net_oi_gex": net_oi_gex,

        # GEX by Volume
        "zero_gamma_vol": float(zero_gamma_vol) if zero_gamma_vol is not None else None,
        "total_vol_call_gex": total_vol_call_gex,
        "total_vol_put_gex": total_vol_put_gex,
        "net_vol_gex": net_vol_gex
    }
