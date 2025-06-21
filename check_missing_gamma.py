#!/usr/bin/env python3
"""
检查Deribit API中缺少Gamma的期权
"""
import requests
from datetime import datetime

DERIBIT_BASE = "https://www.deribit.com/api/v2"

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
    """获取期权数据"""
    response = requests.get(f"{DERIBIT_BASE}/public/ticker", params={"instrument_name": instrument_name})
    data = response.json()
    if "result" in data:
        return data["result"]
    else:
        return None

def check_missing_gamma(currency: str = "BTC"):
    """检查缺少Gamma的期权"""
    print(f"=== 检查{currency}期权缺少Gamma的情况 ===")
    
    # 获取所有期权
    instruments = fetch_instruments(currency)
    
    # 获取最近的到期日
    expirations = sorted(list(set(inst.get("expiration_timestamp") for inst in instruments)))
    closest_expiration_ts = expirations[0]
    closest_expiration_date = datetime.utcfromtimestamp(closest_expiration_ts / 1000).date()
    
    # 过滤指定到期日的期权
    filtered_instruments = [inst for inst in instruments if inst.get("expiration_timestamp") == closest_expiration_ts]
    print(f"检查 {closest_expiration_date} 到期的 {len(filtered_instruments)} 个期权")
    
    missing_gamma_count = 0
    missing_gamma_options = []
    all_greeks_count = 0
    
    for inst in filtered_instruments:
        option_data = fetch_option_data(inst["instrument_name"])
        if option_data is None:
            continue
            
        greeks = option_data.get("greeks", {})
        delta = greeks.get("delta")
        gamma = greeks.get("gamma")
        vega = greeks.get("vega")
        theta = greeks.get("theta")
        
        # 检查是否有所有Greeks
        has_all_greeks = all(x is not None for x in [delta, gamma, vega, theta])
        
        if has_all_greeks:
            all_greeks_count += 1
        else:
            missing_gamma_count += 1
            missing_gamma_options.append({
                "instrument": inst["instrument_name"],
                "strike": inst["strike"],
                "option_type": inst["option_type"],
                "delta": delta,
                "gamma": gamma,
                "vega": vega,
                "theta": theta,
                "mark_iv": option_data.get("mark_iv"),
                "underlying_price": option_data.get("underlying_price")
            })
    
    print(f"\n统计结果:")
    print(f"  有完整Greeks的期权: {all_greeks_count} 个")
    print(f"  缺少Gamma的期权: {missing_gamma_count} 个")
    
    if missing_gamma_options:
        print(f"\n缺少Gamma的期权详情:")
        for i, option in enumerate(missing_gamma_options[:10]):  # 只显示前10个
            print(f"  {i+1}. {option['instrument']}:")
            print(f"     执行价格: {option['strike']}")
            print(f"     期权类型: {option['option_type']}")
            print(f"     Delta: {option['delta']}")
            print(f"     Gamma: {option['gamma']}")
            print(f"     Vega: {option['vega']}")
            print(f"     Theta: {option['theta']}")
            print(f"     隐含波动率: {option['mark_iv']}")
            print(f"     标的价格: {option['underlying_price']}")
            print()
        
        if len(missing_gamma_options) > 10:
            print(f"  ... 还有 {len(missing_gamma_options) - 10} 个期权缺少Gamma")
    
    # 分析缺少Gamma的模式
    if missing_gamma_options:
        print(f"\n缺少Gamma的模式分析:")
        
        # 按期权类型统计
        call_missing = sum(1 for opt in missing_gamma_options if opt['option_type'] == 'call')
        put_missing = sum(1 for opt in missing_gamma_options if opt['option_type'] == 'put')
        print(f"  Call期权缺少Gamma: {call_missing} 个")
        print(f"  Put期权缺少Gamma: {put_missing} 个")
        
        # 按执行价格范围统计
        strikes = [opt['strike'] for opt in missing_gamma_options]
        if strikes:
            min_strike = min(strikes)
            max_strike = max(strikes)
            print(f"  缺少Gamma的执行价格范围: {min_strike} - {max_strike}")
        
        # 检查是否是深度实值或虚值期权
        deep_itm_count = 0
        deep_otm_count = 0
        atm_count = 0
        
        for opt in missing_gamma_options:
            if opt['underlying_price'] and opt['strike']:
                moneyness = opt['underlying_price'] / opt['strike']
                delta = abs(opt['delta']) if opt['delta'] is not None else 0
                
                if delta > 0.95:
                    deep_itm_count += 1
                elif delta < 0.05:
                    deep_otm_count += 1
                else:
                    atm_count += 1
        
        print(f"  深度实值期权 (Delta > 0.95): {deep_itm_count} 个")
        print(f"  深度虚值期权 (Delta < 0.05): {deep_otm_count} 个")
        print(f"  平值期权 (0.05 <= Delta <= 0.95): {atm_count} 个")

if __name__ == "__main__":
    check_missing_gamma("BTC")
    print("\n" + "="*60 + "\n")
    check_missing_gamma("ETH") 