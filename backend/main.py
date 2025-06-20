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

# Use a cache with a 60-second TTL
cache = TTLCache(maxsize=10, ttl=60)

@cached(cache)
def get_processed_gex_data(currency: str):
    """
    Fetches raw option data and spot price, then processes it to get GEX details.
    This function is cached to avoid hitting the API too frequently.
    """
    print(f"Fetching fresh data for {currency}...")
    option_book = fetch_full_option_book(currency)
    spot_price = fetch_spot_price(currency)
    
    if not option_book or spot_price is None:
        raise Exception("Failed to fetch required data from Deribit.")
        
    return calculate_gex_details(option_book, spot_price)

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
        return {"error": str(e)}
