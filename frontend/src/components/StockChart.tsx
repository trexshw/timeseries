import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { format, parseISO } from "date-fns";
import { ChartDataPoint } from "../types/stock";

interface StockChartProps {
  data: ChartDataPoint[];
  symbol: string;
  height?: number;
  showVolume?: boolean;
}

const StockChart: React.FC<StockChartProps> = ({
  data,
  symbol,
  height = 400,
  showVolume = false,
}) => {
  const formatTimestamp = (timestamp: string) => {
    try {
      return format(parseISO(timestamp), "MMM dd HH:mm");
    } catch {
      return timestamp;
    }
  };

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    return volume.toString();
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{formatTimestamp(label)}</p>
          <p className="text-primary-600 font-semibold">
            Price: {formatPrice(payload[0].value)}
          </p>
          {showVolume && payload[1] && (
            <p className="text-gray-600">
              Volume: {formatVolume(payload[1].value)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-gray-50 rounded-lg"
        style={{ height }}
      >
        <p className="text-gray-500">No data available for {symbol}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {symbol} Stock Chart
        </h3>
        <p className="text-sm text-gray-500">{data.length} data points</p>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        {showVolume ? (
          <AreaChart
            data={data}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatTimestamp}
              stroke="#6b7280"
              fontSize={12}
            />
            <YAxis
              yAxisId="left"
              stroke="#3b82f6"
              fontSize={12}
              tickFormatter={formatPrice}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#10b981"
              fontSize={12}
              tickFormatter={formatVolume}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.1}
              yAxisId="left"
            />
            <Area
              type="monotone"
              dataKey="volume"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.1}
              yAxisId="right"
            />
          </AreaChart>
        ) : (
          <LineChart
            data={data}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatTimestamp}
              stroke="#6b7280"
              fontSize={12}
            />
            <YAxis stroke="#3b82f6" fontSize={12} tickFormatter={formatPrice} />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#3b82f6" }}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default StockChart;
