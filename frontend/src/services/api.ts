import axios, { AxiosResponse } from "axios";
import {
  StockDataPoint,
  StockDataBatch,
  TimeRangeQuery,
  StockDataResponse,
  ApiResponse,
} from "../types/stock";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error("API Request Error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error("API Response Error:", error);
    return Promise.reject(error);
  }
);

export const stockApi = {
  // Store single data point
  storeDataPoint: async (
    dataPoint: StockDataPoint
  ): Promise<ApiResponse<any>> => {
    try {
      const response = await apiClient.post("/api/v1/stocks/data", dataPoint);
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  },

  // Store batch data points
  storeDataBatch: async (
    dataBatch: StockDataBatch
  ): Promise<ApiResponse<any>> => {
    try {
      const response = await apiClient.post(
        "/api/v1/stocks/data/batch",
        dataBatch
      );
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  },

  // Query data by time range
  queryData: async (
    query: TimeRangeQuery
  ): Promise<ApiResponse<StockDataResponse>> => {
    try {
      const response = await apiClient.post("/api/v1/stocks/query", query);
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  },

  // Get latest data for a symbol
  getLatestData: async (
    symbol: string,
    limit: number = 100
  ): Promise<ApiResponse<StockDataResponse>> => {
    try {
      const response = await apiClient.get(
        `/api/v1/stocks/${symbol}/latest?limit=${limit}`
      );
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  },

  // Get available symbols
  getSymbols: async (): Promise<ApiResponse<string[]>> => {
    try {
      const response = await apiClient.get("/api/v1/stocks/symbols");
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  },

  // Health check
  healthCheck: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await apiClient.get("/api/v1/stocks/health");
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || error.message };
    }
  },
};

export default apiClient;
