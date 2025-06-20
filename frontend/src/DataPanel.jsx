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
    net_oi_gex,
    // Volume GEX
    zero_gamma_vol,
    net_vol_gex,
    call_wall,
    put_wall,
    max_change_gex
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
          <DataRow label="Net GEX" value={net_oi_gex} unit="M" color={net_oi_gex > 0 ? 'text-green-400' : 'text-red-400'} />
        </div>
        
        {/* GEX by Volume (交易量) */}
        <div>
          <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">GEX by Volume (交易量)</h3>
          <DataRow label="Zero Gamma" value={zero_gamma_vol} color="text-yellow-400" />
          <DataRow label="Major Positive (Call Wall)" value={call_wall} color="text-green-400" />
          <DataRow label="Major Negative (Put Wall)" value={put_wall} color="text-red-400" />
          <DataRow label="Net GEX" value={net_vol_gex} unit="M" color={net_vol_gex > 0 ? 'text-green-400' : 'text-red-400'} />
        </div>

        {/* Max Change GEX */}
        <div>
           <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">Max Change GEX</h3>
           <DataRow label="1 min" value={max_change_gex?.['1min']} color={max_change_gex?.['1min'] > 0 ? 'text-green-400' : 'text-red-400'} />
           <DataRow label="5 min" value={max_change_gex?.['5min']} color={max_change_gex?.['5min'] > 0 ? 'text-green-400' : 'text-red-400'} />
           <DataRow label="10 min" value={max_change_gex?.['10min']} color={max_change_gex?.['10min'] > 0 ? 'text-green-400' : 'text-red-400'} />
           <DataRow label="15 min" value={max_change_gex?.['15min']} color={max_change_gex?.['15min'] > 0 ? 'text-green-400' : 'text-red-400'} />
           <DataRow label="30 min" value={max_change_gex?.['30min']} color={max_change_gex?.['30min'] > 0 ? 'text-green-400' : 'text-red-400'} />
        </div>
      </div>
    </div>
  );
};

export default DataPanel; 