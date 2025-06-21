#!/usr/bin/env python3
import requests
import json

def test_tooltip_data():
    """测试后端API是否返回了新的持仓量和成交量数据字段"""
    try:
        # 测试BTC数据
        response = requests.get("http://localhost:8000/gex?currency=BTC")
        if response.status_code == 200:
            data = response.json()
            print("✅ API响应成功")
            
            if "data" in data and len(data["data"]) > 0:
                print(f"✅ 返回了 {len(data['data'])} 个行权价数据")
                
                # 检查第一个数据点是否包含新字段
                first_item = data["data"][0]
                print(f"第一个行权价: {first_item.get('strike')}")
                
                required_fields = [
                    'call_gex', 'put_gex', 'open_interest', 'volume',
                    'call_oi', 'put_oi', 'call_volume', 'put_volume'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field in first_item:
                        print(f"✅ {field}: {first_item[field]}")
                    else:
                        missing_fields.append(field)
                        print(f"❌ 缺少字段: {field}")
                
                if not missing_fields:
                    print("✅ 所有必需的字段都已返回")
                else:
                    print(f"❌ 缺少字段: {missing_fields}")
                    
                # 显示一些示例数据
                print("\n📊 示例数据:")
                for i, item in enumerate(data["data"][:3]):
                    print(f"  行权价 {item['strike']}:")
                    print(f"    看涨GEX: {item['call_gex']:.2f} M")
                    print(f"    看跌GEX: {item['put_gex']:.2f} M")
                    print(f"    持仓量: {item['open_interest']}")
                    print(f"    成交量: {item['volume']}")
                    print(f"    看涨OI: {item['call_oi']}, 看跌OI: {item['put_oi']}")
                    print(f"    看涨Volume: {item['call_volume']}, 看跌Volume: {item['put_volume']}")
                    print()
            else:
                print("❌ 没有返回数据")
        else:
            print(f"❌ API响应失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_tooltip_data() 