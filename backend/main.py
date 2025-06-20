from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fetcher import fetch_full_option_book, fetch_spot_price
from gex_calc import calculate_gex_details
from cachetools import cached, TTLCache
import json # Import json for pretty printing

app = FastAPI()

# ✅ 允许跨域访问，解决前端（Vercel）访问后端（Railway）被拒问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或限制为你的前端域名，如 "https://gex-frontend.vercel.app"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 设置一个1分钟的缓存
cache = TTLCache(maxsize=10, ttl=60)

@cached(cache)
def get_cached_gex_data(currency: str):
    """带缓存的数据获取函数"""
    print(f"Fetching fresh data for {currency}...")
    option_book = fetch_full_option_book(currency)
    
    # 打印原始数据用于调试
    print("--- Raw Deribit Option Book ---")
    print(json.dumps(option_book, indent=2))
    print("-----------------------------")

    spot_price = fetch_spot_price(currency)
    return calculate_gex_details(option_book, spot_price)

@app.get("/")
def home():
    return {"message": "GEX API is running"}

@app.get("/gex")
def gex(currency: str = "BTC"):
    """
    主接口：返回某币种的 Gamma Exposure 数据
    """
    try:
        return get_cached_gex_data(currency.upper())
    except Exception as e:
        # 清除特定货币的缓存，以便下次可以重试
        cache.pop(currency.upper(), None)
        print(f"Error fetching data for {currency}: {e}")
        return {"error": str(e), "data": []}
