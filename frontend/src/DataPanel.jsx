import React from 'react';

const DataRow = ({ label, value, unit = '', color = 'text-white', precision = 2 }) => (
  <div className="flex justify-between items-center text-sm py-1">
    <span className="text-gray-400">{label}</span>
    <span className={`font-mono font-semibold ${color}`}>
      {typeof value === 'number' ? value.toFixed(precision) : value} {unit}
    </span>
  </div>
);

const DataPanel = ({ apiData }) => {
  if (!apiData) {
    return (
      <div className="w-full md:w-1/3 lg:w-1/4 p-4 bg-gray-800 text-white flex justify-center items-center">
        Loading data...
      </div>
    );
  }

  // Handle case where API returns empty data
  if (!apiData.data || apiData.data.length === 0) {
     return (
      <div className="w-full md:w-1/3 lg:w-1/4 p-4 bg-gray-800 text-white flex justify-center items-center">
        No data received. Waiting for the next update...
      </div>
    );
  }

  const {
    spot_price,
    expiration_date,
    last_update_time,
    // OI GEX
    total_oi_call_gex,
    total_oi_put_gex,
    net_oi_gex,
    // Volume GEX
    zero_gamma_vol,
    total_vol_call_gex,
    total_vol_put_gex,
    net_vol_gex
  } = apiData;

  const updateTime = new Date(last_update_time).toLocaleTimeString();

  return (
    <div className="w-full md:w-1/3 lg:w-1/4 p-4 bg-gray-900 text-white overflow-y-auto">
      <div className="space-y-4">
        {/* Update Section */}
        <div>
          <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">Update</h3>
          <DataRow label="Time" value={updateTime} />
          <DataRow label="Spot" value={spot_price} unit="USD" />
        </div>

        {/* GEX by Open Interest (持仓量) */}
        <div>
          <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">GEX by Open Interest (持仓量)</h3>
          <DataRow label="Major Positive" value={total_oi_call_gex} unit="M" color="text-green-400" />
          <DataRow label="Major Negative" value={total_oi_put_gex} unit="M" color="text-red-400" />
          <DataRow label="Net GEX" value={net_oi_gex} unit="M" color={net_oi_gex > 0 ? 'text-green-400' : 'text-red-400'} />
        </div>
        
        {/* GEX by Volume (交易量) */}
        <div>
          <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">GEX by Volume (交易量)</h3>
          <DataRow label="Zero Gamma" value={zero_gamma_vol} />
          <DataRow label="Major Positive" value={total_vol_call_gex} unit="M" color="text-green-400" />
          <DataRow label="Major Negative" value={total_vol_put_gex} unit="M" color="text-red-400" />
          <DataRow label="Net GEX" value={net_vol_gex} unit="M" color={net_vol_gex > 0 ? 'text-green-400' : 'text-red-400'} />
        </div>

        {/* Placeholder for future use */}
        <div>
           <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">Max Change GEX</h3>
           <DataRow label="1 min" value={"N/A"} />
           <DataRow label="5 min" value={"N/A"} />
           <DataRow label="10 min" value={"N/A"} />
           <DataRow label="15 min" value={"N/A"} />
           <DataRow label="30 min" value={"N/A"} />
        </div>
      </div>
    </div>
  );
};

export default DataPanel; 