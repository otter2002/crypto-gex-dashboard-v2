from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fetcher import get_gex_data, fetch_spot_price
from cachetools import cached, TTLCache
import json # Import json for pretty printing
import os
import redis
import time

app = FastAPI()

# Redis aclient
redis_client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))

# ✅ 允许跨域访问，解决前端（Vercel）访问后端（Railway）被拒问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或限制为你的前端域名，如 "https://gex-frontend.vercel.app"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for 60 seconds
cache = TTLCache(maxsize=10, ttl=60)

@cached(cache)
def get_processed_gex_data(currency: str):
    """
    Fetches and processes GEX data, using Redis for history snapshots.
    """
    print(f"Fetching fresh GEX data for {currency}...")
    gex_details = get_gex_data(currency)
    
    spot_price = fetch_spot_price(currency)
    gex_details["spot_price"] = spot_price
    
    from datetime import datetime
    now_iso = datetime.utcnow().isoformat() + "Z"
    gex_details["last_update_time"] = now_iso
    
    # --- Redis History Snapshot Logic ---
    now_ts = time.time()
    gex_details['timestamp'] = now_ts
    gex_details['currency'] = currency # Add currency to data

    # Store current snapshot in a Redis sorted set
    history_key = f"gex_history:{currency}"
    redis_client.zadd(history_key, {json.dumps(gex_details): now_ts})
    
    # Prune snapshots older than 35 minutes
    redis_client.zremrangebyscore(history_key, "-inf", now_ts - (35 * 60))
    
    # --- Calculate Max Change GEX from Redis ---
    def get_change(minutes_ago):
        target_ts = now_ts - (minutes_ago * 60)
        # Find the latest snapshot before the target time
        past_data_list = redis_client.zrevrangebyscore(history_key, target_ts, "-inf", start=0, num=1)
        
        if past_data_list:
            past_gex = json.loads(past_data_list[0])
            current_net_gex = gex_details.get('net_vol_gex')
            past_net_gex = past_gex.get('net_vol_gex')

            if current_net_gex is not None and past_net_gex is not None:
                return current_net_gex - past_net_gex
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
    Returns calculated GEX data for a given currency.
    """
    try:
        return get_processed_gex_data(currency.upper())
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing /gex request for {currency}: {e}")
        # 在真实错误发生时返回一个包含错误信息的JSON
        return {"error": str(e), "data": [], "last_update_time": None}
