import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer, Legend, CartesianGrid } from "recharts";
import axios from "axios";
import DataPanel from "./DataPanel"; // Import the new panel component

// API基础URL配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const App = () => {
  const [apiData, setApiData] = useState(null);
  const [currency, setCurrency] = useState("BTC");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartY, setDragStartY] = useState(null);
  const [dragStartDomain, setDragStartDomain] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/gex?currency=${currency}`);
      if (response.data && response.data.data && response.data.data.length > 0) {
        setApiData(response.data);
      } // 如果新数据为空，不更新apiData，继续显示旧数据
    } catch (err) {
      setError('Failed to fetch data. Please check the API connection.');
      // 不清空apiData，继续显示旧数据
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // 1分钟刷新
    return () => clearInterval(interval);
  }, [currency]);

  const { data, spot_price, zero_gamma, call_wall, put_wall, expiration_date } = apiData || {};

  // 计算所有相关价格用于Y轴domain
  const allPrices = [
    ...(data ? data.map(d => d.strike) : []),
    spot_price,
    zero_gamma,
    call_wall,
    put_wall
  ].filter(v => typeof v === 'number' && !isNaN(v));
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const padding = (maxPrice - minPrice) * 0.1 || 1000;

  // Y轴缩放与ticks
  const [yDomain, setYDomain] = useState([minPrice - padding, maxPrice + padding]);
  const [ticks, setTicks] = useState([]);

  useEffect(() => {
    // 数据变化时重置domain和ticks
    setYDomain([minPrice - padding, maxPrice + padding]);
    // 自动生成更稀疏的ticks
    const tickStep = Math.max(Math.round((maxPrice - minPrice) / 4 / 1000) * 1000, 2000);
    const newTicks = [];
    for (let p = Math.ceil((minPrice - padding) / tickStep) * tickStep; p <= maxPrice + padding; p += tickStep) {
      newTicks.push(Math.round(p));
    }
    setTicks(newTicks);
  }, [minPrice, maxPrice]);

  // 鼠标滚轮缩放
  const handleWheel = (e) => {
    e.preventDefault();
    const [min, max] = yDomain;
    const center = (min + max) / 2;
    const range = (max - min);
    const zoomFactor = e.deltaY < 0 ? 0.8 : 1.25;
    const newRange = Math.max(range * zoomFactor, 100); // 最小区间100
    setYDomain([center - newRange / 2, center + newRange / 2]);
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStartY(e.clientY);
    setDragStartDomain([...yDomain]);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    const deltaY = e.clientY - dragStartY;
    const chartHeight = document.getElementById('main-chart-area')?.offsetHeight || 400;
    const [min, max] = dragStartDomain;
    const range = max - min;
    const pricePerPixel = range / chartHeight;
    const offset = deltaY * pricePerPixel;
    setYDomain([min + offset, max + offset]);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div
      id="main-chart-area"
      className="flex flex-col md:flex-row h-screen bg-gray-900 text-white"
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      style={{ cursor: isDragging ? 'ns-resize' : 'default' }}
    >
      {/* Main Chart Area */}
      <div className="flex-grow p-4 flex flex-col">
        <div className="flex items-center justify-between mb-4">
            <div>
                <h1 className="text-2xl font-bold">{currency} Gamma Exposure</h1>
                {expiration_date && <h2 className="text-lg text-gray-400">Expiration: {expiration_date}</h2>}
            </div>
            <div className="flex items-center gap-4">
                <select 
                    value={currency} 
                    onChange={e => setCurrency(e.target.value)} 
                    className="border border-gray-600 px-4 py-2 rounded-lg bg-gray-800 text-white shadow-sm"
                >
                    <option value="BTC">BTC</option>
                    <option value="ETH">ETH</option>
                </select>
                <button
                    onClick={fetchData}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-500 text-white px-5 py-2 rounded-lg shadow-sm transition-colors"
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>
        </div>

        {error && <div className="text-red-500 text-center">{error}</div>}
        
        {!apiData && loading && <div className="flex-grow flex justify-center items-center">Loading Chart...</div>}
        
        {apiData && (!data || data.length === 0) && !loading && (
          <div className="flex-grow flex justify-center items-center text-gray-400">
            该币种暂时无期权数据。
          </div>
        )}

        {apiData && data && data.length > 0 && (
          <div className="flex-grow">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={data}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                barCategoryGap="0%"
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9ca3af" domain={['auto', 'auto']} />
                <YAxis type="number" dataKey="strike" stroke="#9ca3af" width={80} reversed={true} domain={yDomain} allowDataOverflow={true} ticks={ticks} />
                <Tooltip
                  cursor={{ fill: 'rgba(156, 163, 175, 0.1)' }}
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }}
                  labelStyle={{ color: '#d1d5db' }}
                />
                <Legend />
                <Bar dataKey="call_gex" fill="#10B981" name="Call GEX" />
                <Bar dataKey="put_gex" fill="#EF4444" name="Put GEX" />

                {/* Reference Lines */}
                {spot_price && <ReferenceLine y={spot_price} label={{ value: `${spot_price.toFixed(2)}`, fill: 'white', position: 'insideTopLeft' }} stroke="white" strokeDasharray="3 3" />}
                {zero_gamma && <ReferenceLine y={zero_gamma} label={{ value: `${zero_gamma.toFixed(2)}`, fill: '#FBBF24', position: 'insideTopLeft' }} stroke="#FBBF24" />}
                {call_wall && <ReferenceLine y={call_wall} label={{ value: `${call_wall}`, fill: '#10B981', position: 'insideTopLeft' }} stroke="#10B981" strokeDasharray="5 5" />}
                {put_wall && <ReferenceLine y={put_wall} label={{ value: `${put_wall}`, fill: '#EF4444', position: 'insideTopLeft' }} stroke="#EF4444" strokeDasharray="5 5" />}
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Data Panel */}
      <DataPanel apiData={apiData} />
    </div>
  );
};

export default App;
