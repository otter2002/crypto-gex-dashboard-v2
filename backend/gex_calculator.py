#!/usr/bin/env python3
import numpy as np
import math
from scipy.stats import norm
from datetime import datetime
import requests
from collections import defaultdict
import concurrent.futures

DERIBIT_BASE = "https://www.deribit.com/api/v2"

def fetch_spot_price(currency: str):
    """获取现货价格"""
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
    else:
        raise Exception(f"Spot price fetch not supported for {currency}")

def fetch_instruments(currency: str):
    """获取所有可用的期权合约"""
    response = requests.get(f"{DERIBIT_BASE}/public/get_instruments", params={
        "currency": currency.upper(),
        "kind": "option",
        "expired": "false"
    })
    data = response.json()
    if "result" in data:
        return data["result"]
    else:
        raise Exception(f"Deribit API error on get_instruments: {data.get('error')}")

def fetch_option_data(instrument_name: str):
    """获取期权数据（价格、隐含波动率等）"""
    response = requests.get(f"{DERIBIT_BASE}/public/ticker", params={"instrument_name": instrument_name})
    data = response.json()
    if "result" in data:
        return data["result"]
    else:
        return None

def black_scholes_greeks(S, K, T, r, sigma, option_type='call'):
    """
    计算Black-Scholes模型的Greeks
    
    参数:
    S: 现货价格
    K: 执行价格
    T: 到期时间（年）
    r: 无风险利率
    sigma: 隐含波动率
    option_type: 'call' 或 'put'
    
    返回:
    dict: 包含delta, gamma, vega, theta的字典
    """
    if T <= 0 or sigma <= 0:
        return {'delta': 0, 'gamma': 0, 'vega': 0, 'theta': 0}
    
    # 计算d1和d2
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    
    # 计算标准正态分布的PDF和CDF
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)
    n_d1 = norm.pdf(d1)
    
    if option_type.lower() == 'call':
        delta = N_d1
        gamma = n_d1 / (S * sigma * np.sqrt(T))
        vega = S * n_d1 * np.sqrt(T)
        theta = (-S * n_d1 * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r*T) * N_d2)
    else:  # put
        delta = N_d1 - 1
        gamma = n_d1 / (S * sigma * np.sqrt(T))
        vega = S * n_d1 * np.sqrt(T)
        theta = (-S * n_d1 * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r*T) * norm.cdf(-d2))
    
    return {
        'delta': delta,
        'gamma': gamma,
        'vega': vega,
        'theta': theta
    }

def calculate_gex_data(currency: str = "BTC"):
    """
    使用完全自定义的Greeks计算GEX数据
    """
    print(f"Calculating GEX for {currency} using custom Greeks...")
    
    # 获取基础数据
    instruments = fetch_instruments(currency)
    spot_price = fetch_spot_price(currency)
    
    if not instruments:
        return {"data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": None}
    
    # 获取最近的到期日
    expirations = sorted(list(set(inst.get("expiration_timestamp") for inst in instruments)))
    if not expirations:
        return {"data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": None}
    
    closest_expiration_ts = expirations[0]
    closest_expiration_date = datetime.utcfromtimestamp(closest_expiration_ts / 1000).date()
    
    # 计算到期时间（年）
    now_ts = datetime.now().timestamp() * 1000
    T = (closest_expiration_ts - now_ts) / (1000 * 365 * 24 * 3600)  # 转换为年
    
    # 无风险利率（可以设置为0或从市场数据获取）
    r = 0.0
    
    print(f"Spot price: {spot_price}, Time to expiry: {T:.4f} years")
    
    # 过滤指定到期日的期权
    filtered_instruments = [inst for inst in instruments if inst.get("expiration_timestamp") == closest_expiration_ts]
    print(f"Processing {len(filtered_instruments)} instruments for {closest_expiration_date}")
    
    # 并发获取期权数据
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        option_data_results = list(executor.map(
            lambda inst: (inst, fetch_option_data(inst["instrument_name"])),
            filtered_instruments
        ))
    
    # 计算GEX
    gex_by_strike = defaultdict(lambda: {
        "oi": {"call_gex": 0, "put_gex": 0}, 
        "vol": {"call_gex": 0, "put_gex": 0},
        "open_interest": {"call": 0, "put": 0},
        "volume": {"call": 0, "put": 0}
    })
    
    processed_count = 0
    skipped_count = 0
    
    for inst, option_data in option_data_results:
        try:
            if option_data is None:
                skipped_count += 1
                continue
                
            strike = inst["strike"]
            is_call = inst["option_type"] == "call"
            oi = option_data.get("open_interest", 0)
            volume = option_data.get("stats", {}).get("volume", 0)
            
            # 获取隐含波动率
            mark_iv = option_data.get("mark_iv", 0)
            if mark_iv <= 0:
                skipped_count += 1
                continue  # 跳过无效的隐含波动率
            
            # 使用Black-Scholes计算Greeks（完全自定义）
            greeks = black_scholes_greeks(
                S=spot_price,
                K=strike,
                T=T,
                r=r,
                sigma=mark_iv/100,  # 转换为小数
                option_type=inst["option_type"]
            )
            
            # 使用自定义计算的Gamma
            gamma = greeks['gamma']
            
            # 计算GEX
            # GEX = Gamma × OI/Volume × (Spot Price)² × Contract Size × 100
            contract_size = inst.get("contract_size", 1.0)
            gex_by_oi_value = gamma * oi * (spot_price**2) * contract_size * 100 / 1_000_000
            gex_by_volume_value = gamma * volume * (spot_price**2) * contract_size * 100 / 1_000_000
            
            if is_call:
                gex_by_strike[strike]["oi"]["call_gex"] += gex_by_oi_value
                gex_by_strike[strike]["vol"]["call_gex"] += gex_by_volume_value
                gex_by_strike[strike]["open_interest"]["call"] += oi
                gex_by_strike[strike]["volume"]["call"] += volume
            else:
                gex_by_strike[strike]["oi"]["put_gex"] += -gex_by_oi_value
                gex_by_strike[strike]["vol"]["put_gex"] += -gex_by_volume_value
                gex_by_strike[strike]["open_interest"]["put"] += oi
                gex_by_strike[strike]["volume"]["put"] += volume
            
            processed_count += 1
                
        except Exception as e:
            print(f"Error processing {inst.get('instrument_name', 'N/A')}: {e}")
            skipped_count += 1
            continue
    
    print(f"Processed: {processed_count}, Skipped: {skipped_count}")
    
    if not gex_by_strike:
        return {"data": [], "zero_gamma": None, "call_wall": None, "put_wall": None, "expiration_date": closest_expiration_date.strftime('%Y-%m-%d')}
    
    # 汇总数据
    strikes = sorted(gex_by_strike.keys())
    data = []
    for s in strikes:
        strike_data = {
            "strike": s, 
            "call_gex": gex_by_strike[s]["vol"]["call_gex"], 
            "put_gex": gex_by_strike[s]["vol"]["put_gex"],
            "open_interest": gex_by_strike[s]["open_interest"]["call"] + gex_by_strike[s]["open_interest"]["put"],
            "volume": gex_by_strike[s]["volume"]["call"] + gex_by_strike[s]["volume"]["put"],
            "call_oi": gex_by_strike[s]["open_interest"]["call"],
            "put_oi": gex_by_strike[s]["open_interest"]["put"],
            "call_volume": gex_by_strike[s]["volume"]["call"],
            "put_volume": gex_by_strike[s]["volume"]["put"]
        }
        data.append(strike_data)
    
    # 计算指标
    total_oi_call_gex = sum(gex_by_strike[s]["oi"]["call_gex"] for s in strikes)
    total_oi_put_gex = sum(gex_by_strike[s]["oi"]["put_gex"] for s in strikes)
    net_oi_gex = total_oi_call_gex + total_oi_put_gex
    
    # Call Wall 和 Put Wall
    call_wall = max(data, key=lambda x: x["call_gex"]) if data else None
    if call_wall:
        call_wall = call_wall["strike"]
    
    put_wall_data = [d for d in data if d["put_gex"] != 0]
    put_wall = min(put_wall_data, key=lambda x: x["put_gex"])["strike"] if put_wall_data else None
    
    # Zero Gamma
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
        pass
    
    # Volume指标
    vol_data = [{"strike": s, "call_gex": gex_by_strike[s]["vol"]["call_gex"], "put_gex": gex_by_strike[s]["vol"]["put_gex"]} for s in strikes]
    total_vol_call_gex = sum(d["call_gex"] for d in vol_data)
    total_vol_put_gex = sum(d["put_gex"] for d in vol_data)
    net_vol_gex = total_vol_call_gex + total_vol_put_gex
    
    # Volume Zero Gamma
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
        "spot_price": spot_price,
        
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