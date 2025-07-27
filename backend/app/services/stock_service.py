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
        """Query stock data within a specified time range."""
        # Build Flux query
        flux_query = self._build_flux_query(query)

        # Execute query
        result = self.db_manager.query(flux_query)

        # Process results
        data_points = self._process_query_results(result)

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
        from(bucket: "{self.db_manager.client.buckets_api().find_bucket_by_name("stock_data").id}")
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

        return f'''
        from(bucket: "{self.db_manager.client.buckets_api().find_bucket_by_name("stock_data").id}")
            |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
            |> filter(fn: (r) => r["_measurement"] == "stock_data")
            |> filter(fn: (r) => r["symbol"] == "{query.symbol}")
            |> aggregateWindow(every: {query.interval}, fn: mean, createEmpty: false)
            |> sort(columns: ["_time"])
        '''

    def _process_query_results(self, result: List[Any]) -> List[Dict[str, Any]]:
        """Process InfluxDB query results into a standardized format."""
        data_points = []

        for table in result:
            for record in table.records:
                data_point = {
                    "timestamp": record.get_time().isoformat(),
                    "price": record.get_value(),
                    "volume": record.values.get("volume", 0)
                }
                data_points.append(data_point)

        return data_points

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
        from(bucket: "{self.db_manager.client.buckets_api().find_bucket_by_name("stock_data").id}")
            |> range(start: -30d)
            |> filter(fn: (r) => r["_measurement"] == "stock_data")
            |> group(columns: ["symbol"])
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
