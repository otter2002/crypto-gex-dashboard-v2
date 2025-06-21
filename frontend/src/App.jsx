import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer, Legend, CartesianGrid } from "recharts";
import axios from "axios";
import DataPanel from "./DataPanel"; // Import the new panel component

// API基础URL配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 自定义Tooltip组件
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-gray-800 border border-gray-600 p-3 rounded-lg shadow-lg max-w-xs">
        <p className="text-white font-bold mb-2">行权价: {label?.toLocaleString()} USD</p>
        <div className="space-y-2">
          <div className="border-b border-gray-600 pb-2">
            <p className="text-green-400 text-sm">
              看涨GEX: {data.call_gex?.toLocaleString(undefined, { maximumFractionDigits: 2 })} M
            </p>
            <p className="text-red-400 text-sm">
              看跌GEX: {data.put_gex?.toLocaleString(undefined, { maximumFractionDigits: 2 })} M
            </p>
            <p className="text-gray-300 text-sm">
              净GEX: {(data.call_gex + data.put_gex)?.toLocaleString(undefined, { maximumFractionDigits: 2 })} M
            </p>
          </div>
          
          {data.open_interest > 0 && (
            <div className="border-b border-gray-600 pb-2">
              <p className="text-blue-400 text-sm font-semibold">持仓量 (OI)</p>
              <p className="text-blue-300 text-xs">看涨: {data.call_oi?.toLocaleString()}</p>
              <p className="text-blue-300 text-xs">看跌: {data.put_oi?.toLocaleString()}</p>
              <p className="text-blue-200 text-xs">总计: {data.open_interest?.toLocaleString()}</p>
            </div>
          )}
          
          {data.volume > 0 && (
            <div>
              <p className="text-yellow-400 text-sm font-semibold">成交量 (Volume)</p>
              <p className="text-yellow-300 text-xs">看涨: {data.call_volume?.toLocaleString()}</p>
              <p className="text-yellow-300 text-xs">看跌: {data.put_volume?.toLocaleString()}</p>
              <p className="text-yellow-200 text-xs">总计: {data.volume?.toLocaleString()}</p>
            </div>
          )}
        </div>
      </div>
    );
  }
  return null;
};

const App = () => {
  const [apiData, setApiData] = useState(null);
  const [currency, setCurrency] = useState("BTC");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartY, setDragStartY] = useState(null);
  const [dragStartDomain, setDragStartDomain] = useState(null);
  const [isMobile, setIsMobile] = useState(false);

  // 检测移动设备
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

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
    // 生成更精确的ticks，移动端使用更少的ticks
    const tickCount = isMobile ? 5 : 8;
    const tickStep = Math.max(Math.round((maxPrice - minPrice) / tickCount / 100) * 100, 500);
    const newTicks = [];
    for (let p = Math.ceil((minPrice - padding) / tickStep) * tickStep; p <= maxPrice + padding; p += tickStep) {
      newTicks.push(Math.round(p));
    }
    setTicks(newTicks);
  }, [minPrice, maxPrice, isMobile]);

  // 鼠标滚轮缩放（桌面端）
  const handleWheel = (e) => {
    if (isMobile) return; // 移动端禁用滚轮缩放
    e.preventDefault();
    const [min, max] = yDomain;
    const center = (min + max) / 2;
    const range = (max - min);
    const zoomFactor = e.deltaY < 0 ? 0.8 : 1.25;
    const newRange = Math.max(range * zoomFactor, 100); // 最小区间100
    setYDomain([center - newRange / 2, center + newRange / 2]);
  };

  // 触摸事件处理（移动端）
  const [touchStartY, setTouchStartY] = useState(null);
  const [touchStartDomain, setTouchStartDomain] = useState(null);

  const handleTouchStart = (e) => {
    if (!isMobile) return;
    setIsDragging(true);
    setTouchStartY(e.touches[0].clientY);
    setTouchStartDomain([...yDomain]);
  };

  const handleTouchMove = (e) => {
    if (!isDragging || !isMobile) return;
    e.preventDefault();
    const deltaY = e.touches[0].clientY - touchStartY;
    const chartHeight = document.getElementById('main-chart-area')?.offsetHeight || 400;
    const [min, max] = touchStartDomain;
    const range = max - min;
    const pricePerPixel = range / chartHeight;
    const offset = deltaY * pricePerPixel;
    setYDomain([min + offset, max + offset]);
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  // 鼠标拖拽（桌面端）
  const handleMouseDown = (e) => {
    if (isMobile) return;
    setIsDragging(true);
    setDragStartY(e.clientY);
    setDragStartDomain([...yDomain]);
  };

  const handleMouseMove = (e) => {
    if (!isDragging || isMobile) return;
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
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{ cursor: isDragging ? 'ns-resize' : 'default' }}
    >
      {/* Main Chart Area */}
      <div className="flex-grow p-2 md:p-4 flex flex-col">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-2">
            <div>
                <h1 className="text-xl md:text-2xl font-bold">{currency} Gamma Exposure</h1>
                {expiration_date && <h2 className="text-sm md:text-lg text-gray-400">Expiration: {expiration_date}</h2>}
            </div>
            <div className="flex items-center gap-2 md:gap-4">
                <select 
                    value={currency} 
                    onChange={e => setCurrency(e.target.value)} 
                    className="border border-gray-600 px-2 md:px-4 py-1 md:py-2 rounded-lg bg-gray-800 text-white shadow-sm text-sm md:text-base"
                >
                    <option value="BTC">BTC</option>
                    <option value="ETH">ETH</option>
                </select>
                <button
                    onClick={fetchData}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-500 text-white px-3 md:px-5 py-1 md:py-2 rounded-lg shadow-sm transition-colors text-sm md:text-base"
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>
        </div>

        {error && <div className="text-red-500 text-center text-sm">{error}</div>}
        
        {!apiData && loading && <div className="flex-grow flex justify-center items-center">Loading Chart...</div>}
        
        {apiData && (!data || data.length === 0) && !loading && (
          <div className="flex-grow flex justify-center items-center text-gray-400">
            该币种暂时无期权数据。
          </div>
        )}

        {apiData && data && data.length > 0 && (
          <div className="flex-grow min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={data}
                margin={{ 
                  top: 20, 
                  right: isMobile ? 10 : 30, 
                  left: isMobile ? 10 : 20, 
                  bottom: 5 
                }}
                barCategoryGap="30%"
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  type="number" 
                  stroke="#9ca3af" 
                  domain={['auto', 'auto']}
                  tickFormatter={(value) => value.toLocaleString()}
                />
                <YAxis 
                  type="number" 
                  dataKey="strike" 
                  stroke="#9ca3af" 
                  width={isMobile ? 60 : 80} 
                  reversed={true} 
                  domain={yDomain} 
                  allowDataOverflow={true} 
                  ticks={ticks}
                  tickFormatter={(value) => value.toLocaleString()}
                />
                <Tooltip
                  content={<CustomTooltip />}
                  cursor={{ fill: 'rgba(156, 163, 175, 0.1)' }}
                />
                <Legend />
                <Bar 
                  dataKey="call_gex" 
                  fill="#10B981" 
                  name="Call GEX" 
                  radius={[0, 2, 2, 0]}
                />
                <Bar 
                  dataKey="put_gex" 
                  fill="#EF4444" 
                  name="Put GEX" 
                  radius={[0, 2, 2, 0]}
                />

                {/* Reference Lines */}
                {spot_price && (
                  <ReferenceLine 
                    y={spot_price} 
                    label={{ 
                      value: `${spot_price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`, 
                      fill: 'white', 
                      position: 'insideTopLeft',
                      fontSize: isMobile ? 10 : 12
                    }} 
                    stroke="white" 
                    strokeDasharray="3 3" 
                  />
                )}
                {zero_gamma && (
                  <ReferenceLine 
                    y={zero_gamma} 
                    label={{ 
                      value: `${zero_gamma.toLocaleString(undefined, { maximumFractionDigits: 2 })}`, 
                      fill: '#FBBF24', 
                      position: 'insideTopLeft',
                      fontSize: isMobile ? 10 : 12
                    }} 
                    stroke="#FBBF24" 
                  />
                )}
                {call_wall && (
                  <ReferenceLine 
                    y={call_wall} 
                    label={{ 
                      value: `${call_wall.toLocaleString(undefined, { maximumFractionDigits: 2 })}`, 
                      fill: '#10B981', 
                      position: 'insideTopLeft',
                      fontSize: isMobile ? 10 : 12
                    }} 
                    stroke="#10B981" 
                    strokeDasharray="5 5" 
                  />
                )}
                {put_wall && (
                  <ReferenceLine 
                    y={put_wall} 
                    label={{ 
                      value: `${put_wall.toLocaleString(undefined, { maximumFractionDigits: 2 })}`, 
                      fill: '#EF4444', 
                      position: 'insideTopLeft',
                      fontSize: isMobile ? 10 : 12
                    }} 
                    stroke="#EF4444" 
                    strokeDasharray="5 5" 
                  />
                )}
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
