#!/usr/bin/env python3
"""
详细检查Gamma值的分布
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

def analyze_gamma_distribution(currency: str = "BTC"):
    """分析Gamma值的分布"""
    print(f"=== 分析{currency}期权Gamma值分布 ===")
    
    # 获取所有期权
    instruments = fetch_instruments(currency)
    
    # 获取最近的到期日
    expirations = sorted(list(set(inst.get("expiration_timestamp") for inst in instruments)))
    closest_expiration_ts = expirations[0]
    closest_expiration_date = datetime.utcfromtimestamp(closest_expiration_ts / 1000).date()
    
    # 过滤指定到期日的期权
    filtered_instruments = [inst for inst in instruments if inst.get("expiration_timestamp") == closest_expiration_ts]
    print(f"分析 {closest_expiration_date} 到期的 {len(filtered_instruments)} 个期权")
    
    gamma_values = []
    zero_gamma_count = 0
    very_small_gamma_count = 0
    normal_gamma_count = 0
    
    for inst in filtered_instruments:
        option_data = fetch_option_data(inst["instrument_name"])
        if option_data is None:
            continue
            
        greeks = option_data.get("greeks", {})
        gamma = greeks.get("gamma")
        delta = greeks.get("delta")
        
        if gamma is not None:
            gamma_values.append(gamma)
            
            if gamma == 0:
                zero_gamma_count += 1
            elif gamma < 0.0001:  # 小于0.0001
                very_small_gamma_count += 1
            else:
                normal_gamma_count += 1
    
    print(f"\nGamma值统计:")
    print(f"  总期权数量: {len(gamma_values)}")
    print(f"  Gamma = 0: {zero_gamma_count} 个")
    print(f"  Gamma < 0.0001: {very_small_gamma_count} 个")
    print(f"  Gamma >= 0.0001: {normal_gamma_count} 个")
    
    if gamma_values:
        print(f"  Gamma最小值: {min(gamma_values)}")
        print(f"  Gamma最大值: {max(gamma_values)}")
        print(f"  Gamma平均值: {sum(gamma_values) / len(gamma_values):.8f}")
    
    # 显示一些具体的Gamma值
    print(f"\nGamma值示例:")
    for i, inst in enumerate(filtered_instruments[:10]):
        option_data = fetch_option_data(inst["instrument_name"])
        if option_data:
            greeks = option_data.get("greeks", {})
            gamma = greeks.get("gamma")
            delta = greeks.get("delta")
            print(f"  {i+1}. {inst['instrument_name']}: Gamma={gamma}, Delta={delta}")
    
    # 检查是否有期权完全没有Gamma字段
    print(f"\n检查API响应结构:")
    sample_option = fetch_option_data(filtered_instruments[0]["instrument_name"])
    if sample_option:
        greeks = sample_option.get("greeks", {})
        print(f"  Greeks字段包含: {list(greeks.keys())}")
        print(f"  完整Greeks响应: {greeks}")

def check_specific_instruments():
    """检查特定的期权合约"""
    print(f"\n=== 检查特定期权合约 ===")
    
    # 检查一些可能有问题的期权
    test_instruments = [
        "BTC-22JUN25-92000-C",
        "BTC-22JUN25-92000-P", 
        "BTC-22JUN25-104000-C",
        "BTC-22JUN25-104000-P",
        "ETH-22JUN25-1500-C",
        "ETH-22JUN25-1500-P",
        "ETH-22JUN25-2450-C",
        "ETH-22JUN25-2450-P"
    ]
    
    for instrument in test_instruments:
        option_data = fetch_option_data(instrument)
        if option_data:
            greeks = option_data.get("greeks", {})
            print(f"\n{instrument}:")
            print(f"  Delta: {greeks.get('delta')}")
            print(f"  Gamma: {greeks.get('gamma')}")
            print(f"  Vega: {greeks.get('vega')}")
            print(f"  Theta: {greeks.get('theta')}")
            print(f"  隐含波动率: {option_data.get('mark_iv')}")
            print(f"  标的价格: {option_data.get('underlying_price')}")

if __name__ == "__main__":
    analyze_gamma_distribution("BTC")
    print("\n" + "="*60 + "\n")
    analyze_gamma_distribution("ETH")
    check_specific_instruments() 