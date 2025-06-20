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
  if (!apiData || !apiData.last_update_time) {
    return (
      <div className="w-full md:w-1/3 lg:w-1/4 p-4 bg-gray-800 text-white flex justify-center items-center">
        Loading data...
      </div>
    );
  }

  const {
    spot_price,
    expiration_date,
    total_call_gex,
    total_put_gex,
    net_gex,
    last_update_time,
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

        {/* Open Interest GEX Section */}
        <div>
          <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">GEX by Open Interest</h3>
          <DataRow label="Major Positive" value={total_call_gex} unit="M" color="text-green-400" />
          <DataRow label="Major Negative" value={total_put_gex} unit="M" color="text-red-400" />
          <DataRow label="Net GEX" value={net_gex} unit="M" color={net_gex > 0 ? 'text-green-400' : 'text-red-400'} />
        </div>
        
        {/* Placeholder sections from screenshot */}
        <div>
          <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">GEX by Volume</h3>
          <DataRow label="Zero Gamma" value={0.00} />
          <DataRow label="Major Positive" value={0.00} />
          <DataRow label="Major Negative" value={0.00} />
          <DataRow label="Net GEX" value={0.00} />
        </div>

        <div>
           <h3 className="font-bold text-lg mb-2 border-b border-gray-700 pb-1">Max Change GEX</h3>
           <DataRow label="1 min" value={0.0} />
           <DataRow label="5 min" value={0.0} />
           <DataRow label="10 min" value={0.0} />
           <DataRow label="15 min" value={0.0} />
           <DataRow label="30 min" value={0.0} />
        </div>
      </div>
    </div>
  );
};

export default DataPanel; 