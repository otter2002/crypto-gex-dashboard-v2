# Crypto Gamma Exposure (GEX) Dashboard

[![Vercel Deployment](https://img.shields.io/badge/Frontend-Vercel-black?style=flat-square&logo=vercel)](https://crypto-gex-dashboard-v2.vercel.app/)
[![Railway Deployment](https://img.shields.io/badge/Backend-Railway-blueviolet?style=flat-square&logo=railway)](https://crypto-gex-dashboard-v2-production.up.railway.app/gex?currency=BTC)
[![Redis](https://img.shields.io/badge/Cache-Redis-red?style=flat-square&logo=redis)](https://redis.io/)

A real-time dashboard for visualizing Gamma Exposure (GEX) of cryptocurrency options (BTC & ETH) from the Deribit exchange. The project provides an interactive chart and detailed data panels to help traders analyze market sentiment and potential volatility points.

![Dashboard Screenshot](https://raw.githubusercontent.com/otter2002/crypto-gex-dashboard-v2/main/screenshot.png) 
*(You may need to add a `screenshot.png` to the root of your repository for the image to display)*

---

## ✨ Core Features

- **Real-Time GEX Data**: Fetches and displays the latest options data for BTC and ETH.
- **Interactive Chart**: 
  - **Zoom**: Use the mouse wheel to zoom in and out of the price (Y-axis).
  - **Pan**: Click and drag the mouse up and down to pan the chart.
  - **Key Levels**: Automatically plots reference lines for Spot Price, Zero Gamma, Call Wall, and Put Wall.
- **Detailed Data Panels**:
  - **GEX by Open Interest**: Shows net GEX calculated from open interest.
  - **GEX by Volume**: Displays GEX calculated from trading volume, along with key price levels.
  - **Max Change GEX**: Calculates and shows the change in Net GEX over 1, 5, 10, 15, and 30-minute intervals, powered by Redis.
- **High-Performance Backend**:
  - **Concurrent API Calls**: Uses `ThreadPoolExecutor` to fetch data for hundreds of option contracts concurrently, significantly improving data refresh speed.
  - **Persistent History**: Leverages **Redis** to store historical GEX snapshots, ensuring robust trend analysis even after service restarts.
- **Auto-Refreshing**: The dashboard automatically fetches new data every minute, with graceful error handling to retain the last valid data.

---

## 🛠️ Tech Stack

- **Frontend**:
  - **Framework**: [React](https://reactjs.org/)
  - **Charting**: [Recharts](https://recharts.org/)
  - **Styling**: [Tailwind CSS](https://tailwindcss.com/)
  - **HTTP Client**: [Axios](https://axios-http.com/)
- **Backend**:
  - **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
  - **Database/Cache**: [Redis](https://redis.io/)
  - **Concurrency**: `concurrent.futures`
- **Deployment**:
  - **Frontend**: [Vercel](https://vercel.com/)
  - **Backend & Redis**: [Railway](https://railway.app/)

---

## 🚀 Getting Started Locally

### Prerequisites

- [Node.js](https://nodejs.org/) (v16+)
- [Python](https://www.python.org/) (v3.8+)
- [Redis](https://redis.io/docs/getting-started/) running locally or a cloud instance URL.

### Backend Setup

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2.  **Create a virtual environment and activate it**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**:
    Create a `.env` file in the `backend` directory with your Redis URL:
    ```
    REDIS_URL=redis://localhost:6379
    ```

5.  **Run the backend server**:
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Set up environment variables**:
    Create a `.env.local` file in the `frontend` directory and point it to your local backend:
    ```
    REACT_APP_API_URL=http://localhost:8000
    ```

4.  **Run the frontend application**:
    ```bash
    npm start
    ```
    The application will open at `http://localhost:3000`.

## API端点

- `GET /` - 健康检查
- `GET /gex?currency=BTC` - 获取指定币种的GEX数据

支持的币种: BTC, ETH, SOL 