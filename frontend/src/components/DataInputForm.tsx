import React, { useState } from "react";
import { useStockData } from "../hooks/useStockData";
import { StockDataPoint } from "../types/stock";

const DataInputForm: React.FC = () => {
  const [formData, setFormData] = useState<StockDataPoint>({
    symbol: "",
    price: 0,
    volume: 0,
    timestamp: new Date().toISOString().slice(0, 16),
  });

  const { useStoreDataPoint } = useStockData();
  const storeDataMutation = useStoreDataPoint();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.symbol && formData.price > 0) {
      storeDataMutation.mutate({
        ...formData,
        timestamp: new Date(formData.timestamp).toISOString(),
      });
      setFormData({
        symbol: "",
        price: 0,
        volume: 0,
        timestamp: new Date().toISOString().slice(0, 16),
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === "price" || name === "volume" ? parseFloat(value) || 0 : value,
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Add Stock Data
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="symbol"
            className="block text-sm font-medium text-gray-700"
          >
            Symbol
          </label>
          <input
            type="text"
            id="symbol"
            name="symbol"
            value={formData.symbol}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="e.g., AAPL"
            required
          />
        </div>

        <div>
          <label
            htmlFor="price"
            className="block text-sm font-medium text-gray-700"
          >
            Price
          </label>
          <input
            type="number"
            id="price"
            name="price"
            value={formData.price}
            onChange={handleInputChange}
            step="0.01"
            min="0"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="0.00"
            required
          />
        </div>

        <div>
          <label
            htmlFor="volume"
            className="block text-sm font-medium text-gray-700"
          >
            Volume
          </label>
          <input
            type="number"
            id="volume"
            name="volume"
            value={formData.volume}
            onChange={handleInputChange}
            min="0"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="0"
            required
          />
        </div>

        <div>
          <label
            htmlFor="timestamp"
            className="block text-sm font-medium text-gray-700"
          >
            Timestamp
          </label>
          <input
            type="datetime-local"
            id="timestamp"
            name="timestamp"
            value={formData.timestamp}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            required
          />
        </div>

        <button
          type="submit"
          disabled={storeDataMutation.isLoading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {storeDataMutation.isLoading ? "Adding..." : "Add Data Point"}
        </button>
      </form>

      {storeDataMutation.isSuccess && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-800">
            Data point added successfully!
          </p>
        </div>
      )}

      {storeDataMutation.isError && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">
            Error:{" "}
            {storeDataMutation.error instanceof Error
              ? storeDataMutation.error.message
              : "An error occurred while adding the data point"}
          </p>
        </div>
      )}
    </div>
  );
};

export default DataInputForm;
