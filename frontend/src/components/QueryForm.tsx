import React, { useState } from "react";
import { TimeRangeQuery } from "../types/stock";

interface QueryFormProps {
  symbols: string[];
  onSubmit: (query: TimeRangeQuery) => void;
  selectedSymbol: string;
}

const QueryForm: React.FC<QueryFormProps> = ({
  symbols,
  onSubmit,
  selectedSymbol,
}) => {
  const [query, setQuery] = useState<TimeRangeQuery>({
    symbol: selectedSymbol,
    interval: "1m",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.symbol) {
      onSubmit(query);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setQuery((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const intervals = [
    { value: "1s", label: "1 Second" },
    { value: "5s", label: "5 Seconds" },
    { value: "10s", label: "10 Seconds" },
    { value: "30s", label: "30 Seconds" },
    { value: "1m", label: "1 Minute" },
    { value: "5m", label: "5 Minutes" },
    { value: "15m", label: "15 Minutes" },
    { value: "30m", label: "30 Minutes" },
    { value: "1h", label: "1 Hour" },
    { value: "4h", label: "4 Hours" },
    { value: "1d", label: "1 Day" },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Query Data</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="query-symbol"
            className="block text-sm font-medium text-gray-700"
          >
            Symbol
          </label>
          <select
            id="query-symbol"
            name="symbol"
            value={query.symbol}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            required
          >
            <option value="">Select a symbol</option>
            {symbols.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="start-time"
            className="block text-sm font-medium text-gray-700"
          >
            Start Time (Optional)
          </label>
          <input
            type="datetime-local"
            id="start-time"
            name="start_time"
            value={query.start_time || ""}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        <div>
          <label
            htmlFor="end-time"
            className="block text-sm font-medium text-gray-700"
          >
            End Time (Optional)
          </label>
          <input
            type="datetime-local"
            id="end-time"
            name="end_time"
            value={query.end_time || ""}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        <div>
          <label
            htmlFor="interval"
            className="block text-sm font-medium text-gray-700"
          >
            Time Interval
          </label>
          <select
            id="interval"
            name="interval"
            value={query.interval}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            required
          >
            {intervals.map((interval) => (
              <option key={interval.value} value={interval.value}>
                {interval.label}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Query Data
        </button>
      </form>

      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-sm text-blue-800">
          <strong>Tip:</strong> Leave start and end times empty to query the
          last 7 days of data.
        </p>
      </div>
    </div>
  );
};

export default QueryForm;
