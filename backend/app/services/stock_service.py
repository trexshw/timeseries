"""Stock data service for handling business logic operations."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from influxdb_client import Point

from app.core.database import db_manager
from app.models.stock_data import StockDataPoint, TimeRangeQuery, StockDataResponse


class StockDataService:
    """Service class for stock data operations."""

    def __init__(self):
        """Initialize the stock data service."""
        self.db_manager = db_manager

    def store_data_point(self, data_point: StockDataPoint) -> None:
        """Store a single stock data point in InfluxDB."""
        point = Point("stock_data") \
            .tag("symbol", data_point.symbol) \
            .field("price", data_point.price) \
            .field("volume", data_point.volume) \
            .time(data_point.timestamp)

        self.db_manager.write_point(point)

    def store_data_batch(self, data_points: List[StockDataPoint]) -> None:
        """Store multiple stock data points in InfluxDB."""
        points = []
        for data_point in data_points:
            point = Point("stock_data") \
                .tag("symbol", data_point.symbol) \
                .field("price", data_point.price) \
                .field("volume", data_point.volume) \
                .time(data_point.timestamp)
            points.append(point)

        self.db_manager.write_points(points)

    def query_data_by_time_range(self, query: TimeRangeQuery) -> StockDataResponse:
        """Query stock data by time range."""
        # Get price data
        price_query = self._build_flux_query(query)
        price_result = self.db_manager.query(price_query)
        price_data = self._process_price_results(price_result)

        # Get volume data
        volume_query = self._build_volume_query(query)
        volume_result = self.db_manager.query(volume_query)
        volume_data = self._process_volume_results(volume_result)

        # Combine price and volume data
        data_points = self._combine_price_and_volume(price_data, volume_data)

        # Determine time range
        time_range = self._determine_time_range(query)

        return StockDataResponse(
            symbol=query.symbol,
            data_points=data_points,
            total_points=len(data_points),
            time_range=time_range,
            interval=query.interval
        )

    def query_latest_data(self, symbol: str, limit: int = 100) -> StockDataResponse:
        """Query the latest stock data for a symbol."""
        query = TimeRangeQuery(
            symbol=symbol,
            interval="1m"
        )

        # Build Flux query for latest data
        flux_query = f'''
        from(bucket: "stock_data")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "stock_data")
            |> filter(fn: (r) => r["symbol"] == "{symbol}")
            |> sort(columns: ["_time"], desc: true)
            |> limit(n: {limit})
        '''

        result = self.db_manager.query(flux_query)
        data_points = self._process_query_results(result)

        return StockDataResponse(
            symbol=symbol,
            data_points=data_points,
            total_points=len(data_points),
            time_range={"start": datetime.utcnow() - timedelta(hours=1), "end": datetime.utcnow()},
            interval="1m"
        )

    def _build_flux_query(self, query: TimeRangeQuery) -> str:
        """Build Flux query string for time range queries."""
        start_time = query.start_time or datetime.utcnow() - timedelta(days=7)
        end_time = query.end_time or datetime.utcnow()

        # Format datetime for Flux query (RFC3339 format)
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        return f'''
        from(bucket: "stock_data")
            |> range(start: {start_str}, stop: {end_str})
            |> filter(fn: (r) => r["_measurement"] == "stock_data")
            |> filter(fn: (r) => r["symbol"] == "{query.symbol}")
            |> filter(fn: (r) => r["_field"] == "price")
            |> aggregateWindow(every: {query.interval}, fn: mean, createEmpty: false)
            |> sort(columns: ["_time"])
        '''

    def _build_volume_query(self, query: TimeRangeQuery) -> str:
        """Build Flux query string for volume data."""
        start_time = query.start_time or datetime.utcnow() - timedelta(days=7)
        end_time = query.end_time or datetime.utcnow()

        # Format datetime for Flux query (RFC3339 format)
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        return f'''
        from(bucket: "stock_data")
            |> range(start: {start_str}, stop: {end_str})
            |> filter(fn: (r) => r["_measurement"] == "stock_data")
            |> filter(fn: (r) => r["symbol"] == "{query.symbol}")
            |> filter(fn: (r) => r["_field"] == "volume")
            |> aggregateWindow(every: {query.interval}, fn: sum, createEmpty: false)
            |> sort(columns: ["_time"])
        '''

    def _process_query_results(self, result: List[Any]) -> List[Dict[str, Any]]:
        """Process InfluxDB query results into a standardized format."""
        data_points = []

        for table in result:
            for record in table.records:
                # With pivot, we get both price and volume in the same record
                data_point = {
                    "timestamp": record.get_time().isoformat(),
                    "price": record.values.get("price", 0),
                    "volume": record.values.get("volume", 0)
                }
                data_points.append(data_point)

        return data_points

    def _process_price_results(self, result: List[Any]) -> List[Dict[str, Any]]:
        """Process InfluxDB query results for price data."""
        price_data = []
        for table in result:
            for record in table.records:
                price_data.append({
                    "timestamp": record.get_time().isoformat(),
                    "price": record.get_value()
                })
        return price_data

    def _process_volume_results(self, result: List[Any]) -> List[Dict[str, Any]]:
        """Process InfluxDB query results for volume data."""
        volume_data = []
        for table in result:
            for record in table.records:
                volume_data.append({
                    "timestamp": record.get_time().isoformat(),
                    "volume": record.get_value()
                })
        return volume_data

    def _combine_price_and_volume(self, price_data: List[Dict[str, Any]], volume_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine price and volume data points based on timestamp."""
        combined_data = []
        price_index = 0
        volume_index = 0

        while price_index < len(price_data) and volume_index < len(volume_data):
            price_point = price_data[price_index]
            volume_point = volume_data[volume_index]

            if price_point["timestamp"] == volume_point["timestamp"]:
                combined_data.append({
                    "timestamp": price_point["timestamp"],
                    "price": price_point["price"],
                    "volume": volume_point["volume"]
                })
                price_index += 1
                volume_index += 1
            elif price_point["timestamp"] < volume_point["timestamp"]:
                combined_data.append(price_point)
                price_index += 1
            else:
                combined_data.append(volume_point)
                volume_index += 1

        # Add remaining price points
        while price_index < len(price_data):
            combined_data.append(price_data[price_index])
            price_index += 1

        # Add remaining volume points
        while volume_index < len(volume_data):
            combined_data.append(volume_data[volume_index])
            volume_index += 1

        return combined_data

    def _determine_time_range(self, query: TimeRangeQuery) -> Dict[str, datetime]:
        """Determine the actual time range for the query."""
        start_time = query.start_time or datetime.utcnow() - timedelta(days=7)
        end_time = query.end_time or datetime.utcnow()

        return {
            "start": start_time,
            "end": end_time
        }

    def get_available_symbols(self) -> List[str]:
        """Get list of available stock symbols in the database."""
        flux_query = f'''
        from(bucket: "stock_data")
            |> range(start: -30d)
            |> filter(fn: (r) => r["_measurement"] == "stock_data")
            |> distinct(column: "symbol")
        '''

        result = self.db_manager.query(flux_query)
        symbols = []

        for table in result:
            for record in table.records:
                symbols.append(record.values.get("symbol"))

        return list(set(symbols))


# Global service instance
stock_service = StockDataService()
