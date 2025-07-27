export interface StockDataPoint {
  symbol: string;
  price: number;
  volume: number;
  timestamp: string;
}

export interface StockDataBatch {
  data_points: StockDataPoint[];
}

export interface TimeRangeQuery {
  symbol: string;
  start_time?: string;
  end_time?: string;
  interval: string;
}

export interface StockDataResponse {
  symbol: string;
  data_points: Array<{
    timestamp: string;
    price: number;
    volume: number;
  }>;
  total_points: number;
  time_range: {
    start: string;
    end: string;
  };
  interval: string;
}

export interface ChartDataPoint {
  timestamp: string;
  price: number;
  volume: number;
}

export interface StockSymbol {
  symbol: string;
  name?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}
