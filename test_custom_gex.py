#!/usr/bin/env python3
"""
测试自定义GEX计算器
"""
from backend.gex_calculator import calculate_gex_data, black_scholes_greeks

def test_greeks_calculation():
    """测试Black-Scholes Greeks计算"""
    print("=== 测试Black-Scholes Greeks计算 ===")
    
    # 测试参数
    S = 100000  # 现货价格
    K = 100000  # 执行价格（平值期权）
    T = 0.1     # 到期时间（年）
    r = 0.0     # 无风险利率
    sigma = 0.8 # 隐含波动率（80%）
    
    print(f"现货价格: {S}")
    print(f"执行价格: {K}")
    print(f"到期时间: {T} 年")
    print(f"无风险利率: {r}")
    print(f"隐含波动率: {sigma}")
    
    # 计算Call期权Greeks
    call_greeks = black_scholes_greeks(S, K, T, r, sigma, 'call')
    print(f"\nCall期权Greeks:")
    print(f"  Delta: {call_greeks['delta']:.6f}")
    print(f"  Gamma: {call_greeks['gamma']:.6f}")
    print(f"  Vega: {call_greeks['vega']:.6f}")
    print(f"  Theta: {call_greeks['theta']:.6f}")
    
    # 计算Put期权Greeks
    put_greeks = black_scholes_greeks(S, K, T, r, sigma, 'put')
    print(f"\nPut期权Greeks:")
    print(f"  Delta: {put_greeks['delta']:.6f}")
    print(f"  Gamma: {put_greeks['gamma']:.6f}")
    print(f"  Vega: {put_greeks['vega']:.6f}")
    print(f"  Theta: {put_greeks['theta']:.6f}")
    
    # 验证Gamma应该相同
    print(f"\n验证: Call和Put的Gamma应该相同: {call_greeks['gamma'] == put_greeks['gamma']}")

def test_gex_calculation():
    """测试GEX计算"""
    print("\n=== 测试GEX计算 ===")
    
    # 测试BTC
    print("\n--- BTC GEX ---")
    try:
        btc_result = calculate_gex_data('BTC')
        print(f"数据点数量: {len(btc_result['data'])}")
        print(f"到期日: {btc_result['expiration_date']}")
        print(f"现货价格: {btc_result['spot_price']}")
        print(f"Zero Gamma: {btc_result['zero_gamma']}")
        print(f"Call Wall: {btc_result['call_wall']}")
        print(f"Put Wall: {btc_result['put_wall']}")
        print(f"总Call GEX (OI): {btc_result['total_oi_call_gex']:.2f}")
        print(f"总Put GEX (OI): {btc_result['total_oi_put_gex']:.2f}")
        print(f"净GEX (OI): {btc_result['net_oi_gex']:.2f}")
        print(f"总Call GEX (Volume): {btc_result['total_vol_call_gex']:.2f}")
        print(f"总Put GEX (Volume): {btc_result['total_vol_put_gex']:.2f}")
        print(f"净GEX (Volume): {btc_result['net_vol_gex']:.2f}")
    except Exception as e:
        print(f"BTC GEX计算错误: {e}")
    
    # 测试ETH
    print("\n--- ETH GEX ---")
    try:
        eth_result = calculate_gex_data('ETH')
        print(f"数据点数量: {len(eth_result['data'])}")
        print(f"到期日: {eth_result['expiration_date']}")
        print(f"现货价格: {eth_result['spot_price']}")
        print(f"Zero Gamma: {eth_result['zero_gamma']}")
        print(f"Call Wall: {eth_result['call_wall']}")
        print(f"Put Wall: {eth_result['put_wall']}")
        print(f"总Call GEX (OI): {eth_result['total_oi_call_gex']:.2f}")
        print(f"总Put GEX (OI): {eth_result['total_oi_put_gex']:.2f}")
        print(f"净GEX (OI): {eth_result['net_oi_gex']:.2f}")
        print(f"总Call GEX (Volume): {eth_result['total_vol_call_gex']:.2f}")
        print(f"总Put GEX (Volume): {eth_result['total_vol_put_gex']:.2f}")
        print(f"净GEX (Volume): {eth_result['net_vol_gex']:.2f}")
    except Exception as e:
        print(f"ETH GEX计算错误: {e}")

if __name__ == "__main__":
    test_greeks_calculation()
    test_gex_calculation() 