from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fetcher import fetch_full_option_book, fetch_spot_price
# from gex_calc import calculate_gex_details # Temporarily disabled
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

# Use a very short cache for debugging
cache = TTLCache(maxsize=10, ttl=5)

# @cached(cache) # Disable cache for debugging
def get_raw_deribit_data(currency: str):
    """A temporary function to return raw data for debugging."""
    print(f"Fetching raw data for {currency}...")
    option_book = fetch_full_option_book(currency)
    # Just return the raw data
    return option_book

@app.get("/")
def home():
    return {"message": "GEX API is in DEBUG MODE"}

@app.get("/gex")
def gex(currency: str = "BTC"):
    """
    DEBUGGING ENDPOINT: Returns raw data from Deribit
    """
    try:
        return get_raw_deribit_data(currency.upper())
    except Exception as e:
        return {"error": str(e)}
