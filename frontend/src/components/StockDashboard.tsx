import React, { useState } from "react";
import { useStockData } from "../hooks/useStockData";
import StockChart from "./StockChart";
import DataInputForm from "./DataInputForm";
import QueryForm from "./QueryForm";
import { TimeRangeQuery, ChartDataPoint } from "../types/stock";

const StockDashboard: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>("");
  const [queryParams, setQueryParams] = useState<TimeRangeQuery | null>(null);

  const { useSymbols, useLatestData, useTimeRangeData, useHealthCheck } =
    useStockData();

  const { data: symbols, isLoading: symbolsLoading } = useSymbols();
  const { data: latestData, isLoading: latestLoading } =
    useLatestData(selectedSymbol);
  const { data: timeRangeData, isLoading: timeRangeLoading } = useTimeRangeData(
    queryParams || { symbol: "", interval: "1m" }
  );
  const { data: healthData } = useHealthCheck();

  const handleSymbolSelect = (symbol: string) => {
    setSelectedSymbol(symbol);
    setQueryParams(null);
  };

  const handleQuerySubmit = (query: TimeRangeQuery) => {
    setQueryParams(query);
  };

  const getChartData = (): ChartDataPoint[] => {
    if (timeRangeData) {
      return timeRangeData.data_points.map((point) => ({
        timestamp: point.timestamp,
        price: point.price,
        volume: point.volume,
      }));
    }

    if (latestData) {
      return latestData.data_points.map((point) => ({
        timestamp: point.timestamp,
        price: point.price,
        volume: point.volume,
      }));
    }

    return [];
  };

  const isLoading = symbolsLoading || latestLoading || timeRangeLoading;

  return (
    <div className="space-y-6">
      {/* Health Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  healthData?.status === "healthy"
                    ? "bg-green-500"
                    : "bg-red-500"
                }`}
              ></div>
              <span className="text-sm text-gray-600">
                {healthData?.status === "healthy" ? "Healthy" : "Unhealthy"}
              </span>
            </div>
            {healthData?.database_connected && (
              <span className="text-sm text-green-600">Database Connected</span>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Controls */}
        <div className="space-y-6">
          {/* Symbol Selection */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Available Symbols
            </h3>
            {symbolsLoading ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                {symbols?.map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => handleSymbolSelect(symbol)}
                    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      selectedSymbol === symbol
                        ? "bg-primary-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {symbol}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Data Input Form */}
          <DataInputForm />

          {/* Query Form */}
          <QueryForm
            symbols={symbols || []}
            onSubmit={handleQuerySubmit}
            selectedSymbol={selectedSymbol}
          />
        </div>

        {/* Right Column - Chart */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedSymbol
                  ? `${selectedSymbol} Stock Chart`
                  : "Select a symbol to view data"}
              </h3>
              {isLoading && (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                  <span className="text-sm text-gray-500">Loading...</span>
                </div>
              )}
            </div>

            {selectedSymbol ? (
              <StockChart
                data={getChartData()}
                symbol={selectedSymbol}
                height={400}
                showVolume={true}
              />
            ) : (
              <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
                <div className="text-center">
                  <div className="text-gray-400 text-6xl mb-4">📈</div>
                  <p className="text-gray-500">
                    Select a stock symbol to view the chart
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDashboard;
