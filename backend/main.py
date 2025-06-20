from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fetcher import get_gex_data  # 确保 fetcher.py 中有该函数

app = FastAPI()

# ✅ 允许跨域访问，解决前端（Vercel）访问后端（Railway）被拒问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或限制为你的前端域名，如 "https://gex-frontend.vercel.app"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "GEX API is running"}

@app.get("/gex")
def gex(currency: str = "BTC"):
    """
    主接口：返回某币种的 Gamma Exposure 数据
    """
    try:
        return get_gex_data(currency.upper())
    except Exception as e:
        return {
            "error": str(e),
            "data": [],
            "zero_gamma": None,
            "call_wall": None,
            "put_wall": None
        }
