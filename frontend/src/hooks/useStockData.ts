import { useQuery, useMutation, useQueryClient } from "react-query";
import { stockApi } from "../services/api";
import {
  StockDataPoint,
  StockDataBatch,
  TimeRangeQuery,
  StockDataResponse,
} from "../types/stock";

export const useStockData = () => {
  const queryClient = useQueryClient();

  // Query for available symbols
  const useSymbols = () => {
    return useQuery("symbols", async () => {
      const response = await stockApi.getSymbols();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data || [];
    });
  };

  // Query for latest data
  const useLatestData = (symbol: string, limit: number = 100) => {
    return useQuery(
      ["latestData", symbol, limit],
      async () => {
        const response = await stockApi.getLatestData(symbol, limit);
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data;
      },
      {
        enabled: !!symbol,
        refetchInterval: 30000, // Refetch every 30 seconds
      }
    );
  };

  // Query for time range data
  const useTimeRangeData = (query: TimeRangeQuery) => {
    return useQuery(
      ["timeRangeData", query],
      async () => {
        const response = await stockApi.queryData(query);
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data;
      },
      {
        enabled: !!query.symbol,
      }
    );
  };

  // Mutation for storing single data point
  const useStoreDataPoint = () => {
    return useMutation(
      async (dataPoint: StockDataPoint) => {
        const response = await stockApi.storeDataPoint(dataPoint);
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data;
      },
      {
        onSuccess: () => {
          // Invalidate and refetch relevant queries
          queryClient.invalidateQueries(["latestData"]);
          queryClient.invalidateQueries(["timeRangeData"]);
        },
      }
    );
  };

  // Mutation for storing batch data
  const useStoreDataBatch = () => {
    return useMutation(
      async (dataBatch: StockDataBatch) => {
        const response = await stockApi.storeDataBatch(dataBatch);
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data;
      },
      {
        onSuccess: () => {
          // Invalidate and refetch relevant queries
          queryClient.invalidateQueries(["latestData"]);
          queryClient.invalidateQueries(["timeRangeData"]);
          queryClient.invalidateQueries("symbols");
        },
      }
    );
  };

  // Health check query
  const useHealthCheck = () => {
    return useQuery(
      "healthCheck",
      async () => {
        const response = await stockApi.healthCheck();
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data;
      },
      {
        refetchInterval: 60000, // Check health every minute
      }
    );
  };

  return {
    useSymbols,
    useLatestData,
    useTimeRangeData,
    useStoreDataPoint,
    useStoreDataBatch,
    useHealthCheck,
  };
};
