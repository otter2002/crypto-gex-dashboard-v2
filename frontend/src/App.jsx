import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import axios from "axios";

// API基础URL配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const App = () => {
  const [data, setData] = useState([]);
  const [currency, setCurrency] = useState("BTC");
  const [zeroGamma, setZeroGamma] = useState(null);
  const [callWall, setCallWall] = useState(null);
  const [putWall, setPutWall] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/gex?currency=${currency}`);
      setData(response.data.data);
      setZeroGamma(response.data.zero_gamma);
      setCallWall(response.data.call_wall);
      setPutWall(response.data.put_wall);
    } catch (err) {
      console.error('API Error:', err);
      setError('获取数据失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // 每30秒刷新一次
    return () => clearInterval(interval);
  }, [currency]);

  return (
    <div className="p-4 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">{currency} Gamma Exposure Dashboard</h1>
      
      <div className="mb-6 flex gap-4 justify-center items-center">
        <select 
          value={currency} 
          onChange={e => setCurrency(e.target.value)} 
          className="border px-4 py-2 rounded-lg bg-white shadow-sm"
        >
          <option value="BTC">Bitcoin (BTC)</option>
          <option value="ETH">Ethereum (ETH)</option>
          <option value="SOL">Solana (SOL)</option>
        </select>
        <button
          onClick={fetchData}
          disabled={loading}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg shadow-sm transition-colors"
        >
          {loading ? '🔄 加载中...' : '🔄 手动刷新'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {loading && data.length === 0 ? (
        <div className="flex justify-center items-center h-96">
          <div className="text-xl text-gray-500">加载中...</div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <XAxis 
                dataKey="strike" 
                type="number" 
                domain={["auto", "auto"]}
                label={{ value: 'Strike Price', position: 'insideBottom', offset: -10 }}
              />
              <YAxis 
                label={{ value: 'Gamma Exposure', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                formatter={(value, name) => [
                  value?.toLocaleString() || value, 
                  name === 'call_gex' ? 'Call GEX' : 'Put GEX'
                ]}
                labelFormatter={(label) => `Strike: ${label}`}
              />
              <Bar dataKey="call_gex" fill="#4ade80" stackId="gex" name="Call GEX" />
              <Bar dataKey="put_gex" fill="#f87171" stackId="gex" name="Put GEX" />
              {zeroGamma && (
                <ReferenceLine 
                  x={zeroGamma} 
                  stroke="#facc15" 
                  strokeWidth={2}
                  label={{ value: "Zero Gamma", position: "top" }}
                />
              )} 
              {callWall && (
                <ReferenceLine 
                  x={callWall} 
                  stroke="#22c55e" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  label={{ value: "Call Wall", position: "top" }}
                />
              )} 
              {putWall && (
                <ReferenceLine 
                  x={putWall} 
                  stroke="#ef4444" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  label={{ value: "Put Wall", position: "top" }}
                />
              )} 
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default App;
