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

  return (
    <div className="flex flex-col md:flex-row h-screen bg-gray-900 text-white">
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
                    <option value="SOL">SOL</option>
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
            No chart data available. The API may be fetching new data.
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
                <YAxis type="number" dataKey="strike" stroke="#9ca3af" width={80} reversed={true} />
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
