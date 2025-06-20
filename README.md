# Crypto GEX Dashboard

一个实时显示加密货币Gamma Exposure数据的仪表板。

## 项目结构

```
crypto-gex-dashboard-v2/
├── backend/          # FastAPI后端 (部署到Railway)
│   ├── main.py       # FastAPI应用入口
│   ├── fetcher.py    # 数据获取逻辑
│   ├── gex_calc.py   # GEX计算逻辑
│   ├── requirements.txt
│   └── start.sh
└── frontend/         # React前端 (部署到Vercel)
    └── src/
        └── App.jsx
```

## 部署状态

- **前端**: [![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)
- **后端**: [![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)

## 本地开发

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 前端
```bash
cd frontend
npm install
npm start
```

## API端点

- `GET /` - 健康检查
- `GET /gex?currency=BTC` - 获取指定币种的GEX数据

支持的币种: BTC, ETH, SOL 