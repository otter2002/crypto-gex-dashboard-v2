#!/usr/bin/env python3
"""
调试GEX计算中的过滤逻辑
"""
from backend.gex_calculator import fetch_instruments, fetch_option_data, black_scholes_greeks
from datetime import datetime
import requests

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

def debug_gex_filtering(currency: str = "BTC"):
    """调试GEX计算中的过滤逻辑"""
    print(f"=== 调试{currency} GEX过滤逻辑 ===")
    
    # 获取基础数据
    instruments = fetch_instruments(currency)
    spot_price = fetch_spot_price(currency)
    
    # 获取最近的到期日
    expirations = sorted(list(set(inst.get("expiration_timestamp") for inst in instruments)))
    closest_expiration_ts = expirations[0]
    closest_expiration_date = datetime.utcfromtimestamp(closest_expiration_ts / 1000).date()
    
    # 计算到期时间（年）
    now_ts = datetime.now().timestamp() * 1000
    T = (closest_expiration_ts - now_ts) / (1000 * 365 * 24 * 3600)
    
    print(f"现货价格: {spot_price}")
    print(f"到期时间: {T:.4f} 年")
    print(f"到期日: {closest_expiration_date}")
    
    # 过滤指定到期日的期权
    filtered_instruments = [inst for inst in instruments if inst.get("expiration_timestamp") == closest_expiration_ts]
    print(f"\n过滤后的期权数量: {len(filtered_instruments)}")
    
    # 分析每个期权的处理情况
    processed_count = 0
    skipped_count = 0
    skipped_reasons = {}
    
    for inst in filtered_instruments:
        try:
            option_data = fetch_option_data(inst["instrument_name"])
            if option_data is None:
                skipped_count += 1
                reason = "API返回空数据"
                skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1
                continue
            
            # 获取隐含波动率
            mark_iv = option_data.get("mark_iv", 0)
            if mark_iv <= 0:
                skipped_count += 1
                reason = f"无效隐含波动率: {mark_iv}"
                skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1
                continue
            
            # 尝试计算Greeks
            try:
                greeks = black_scholes_greeks(
                    S=spot_price,
                    K=inst["strike"],
                    T=T,
                    r=0.0,
                    sigma=mark_iv/100,
                    option_type=inst["option_type"]
                )
                processed_count += 1
            except Exception as e:
                skipped_count += 1
                reason = f"Greeks计算失败: {str(e)}"
                skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1
                
        except Exception as e:
            skipped_count += 1
            reason = f"处理异常: {str(e)}"
            skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1
    
    print(f"\n处理结果:")
    print(f"  成功处理: {processed_count} 个期权")
    print(f"  跳过处理: {skipped_count} 个期权")
    
    if skipped_reasons:
        print(f"\n跳过原因:")
        for reason, count in skipped_reasons.items():
            print(f"  {reason}: {count} 个")
    
    # 按执行价格分组统计
    strikes = {}
    for inst in filtered_instruments:
        strike = inst["strike"]
        if strike not in strikes:
            strikes[strike] = {"call": None, "put": None}
        
        option_data = fetch_option_data(inst["instrument_name"])
        if option_data and option_data.get("mark_iv", 0) > 0:
            strikes[strike][inst["option_type"]] = option_data.get("mark_iv", 0)
    
    print(f"\n执行价格隐含波动率分布:")
    for strike in sorted(strikes.keys()):
        call_iv = strikes[strike]["call"]
        put_iv = strikes[strike]["put"]
        print(f"  {strike}: Call IV={call_iv}, Put IV={put_iv}")

if __name__ == "__main__":
    debug_gex_filtering("BTC")
    print("\n" + "="*50 + "\n")
    debug_gex_filtering("ETH") 