import requests
from collections import defaultdict
import numpy as np
from datetime import datetime, date
import concurrent.futures
from gex_calculator import calculate_gex_data

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
    """
    使用自定义GEX计算器获取GEX数据
    """
    return calculate_gex_data(currency)
