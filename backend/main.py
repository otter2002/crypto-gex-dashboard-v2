from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fetcher import get_gex_data, fetch_spot_price
from cachetools import cached, TTLCache
import json # Import json for pretty printing
from collections import deque
import time

app = FastAPI()

# ✅ 允许跨域访问，解决前端（Vercel）访问后端（Railway）被拒问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或限制为你的前端域名，如 "https://gex-frontend.vercel.app"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use a cache with a 60-second TTL
cache = TTLCache(maxsize=10, ttl=60)

# 保存最近30分钟的快照（每分钟一条，最大32条）
gex_history = deque(maxlen=32)

@cached(cache)
def get_processed_gex_data(currency: str):
    """
    直接调用 fetcher.py 中完整的GEX计算逻辑。
    这个函数被缓存以提高性能。
    """
    print(f"Fetching fresh GEX data for {currency}...")
    # get_gex_data 已经包含了所有获取和计算的逻辑
    gex_details = get_gex_data(currency)
    
    # 我们仍然可以单独获取现货价格并添加到最终结果中，以便前端使用
    spot_price = fetch_spot_price(currency)
    
    # 将现货价格和最后更新时间添加到结果中
    gex_details["spot_price"] = spot_price
    from datetime import datetime
    gex_details["last_update_time"] = datetime.utcnow().isoformat() + "Z"
    
    now = time.time()
    gex_details['timestamp'] = now
    gex_history.append(gex_details)
    
    # 计算max change
    def get_change(minutes):
        past = [x for x in gex_history if now - x['timestamp'] >= minutes*60 and x.get('currency') == currency]
        if past:
            return gex_details.get('net_vol_gex') - past[-1].get('net_vol_gex')
        return None
    gex_details['max_change_gex'] = {
        '1min': get_change(1),
        '5min': get_change(5),
        '10min': get_change(10),
        '15min': get_change(15),
        '30min': get_change(30),
    }
    
    return gex_details

@app.get("/")
def home():
    return {"message": "GEX API is operational"}

@app.get("/gex")
def gex(currency: str = "BTC"):
    """
    返回指定货币的GEX计算结果。
    """
    try:
        # 统一使用大写
        return get_processed_gex_data(currency.upper())
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing /gex request for {currency}: {e}")
        # 在真实错误发生时返回一个包含错误信息的JSON
        return {"error": str(e), "data": [], "last_update_time": None}
