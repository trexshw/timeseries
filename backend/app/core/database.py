"""Database connection and client management for InfluxDB."""

from typing import Optional
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.query_api import QueryApi

from app.core.config import settings


class InfluxDBManager:
    """Manager class for InfluxDB operations."""

    def __init__(self):
        """Initialize InfluxDB client."""
        self.client: Optional[InfluxDBClient] = None
        self.write_api = None
        self.query_api = None
        self._connect()

    def _connect(self) -> None:
        """Establish connection to InfluxDB."""
        try:
            self.client = InfluxDBClient(
                url=settings.influxdb_url,
                token=settings.influxdb_token,
                org=settings.influxdb_org
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to InfluxDB: {e}")

    def write_point(self, point: Point) -> None:
        """Write a single data point to InfluxDB."""
        if not self.write_api:
            raise RuntimeError("Write API not initialized")

        try:
            self.write_api.write(
                bucket=settings.influxdb_bucket,
                record=point
            )
        except Exception as e:
            raise RuntimeError(f"Failed to write point to InfluxDB: {e}")

    def write_points(self, points: list[Point]) -> None:
        """Write multiple data points to InfluxDB."""
        if not self.write_api:
            raise RuntimeError("Write API not initialized")

        try:
            self.write_api.write(
                bucket=settings.influxdb_bucket,
                record=points
            )
        except Exception as e:
            raise RuntimeError(f"Failed to write points to InfluxDB: {e}")

    def query(self, query: str) -> list:
        """Execute a Flux query and return results."""
        if not self.query_api:
            raise RuntimeError("Query API not initialized")

        try:
            result = self.query_api.query(query=query, org=settings.influxdb_org)
            return list(result)
        except Exception as e:
            raise RuntimeError(f"Failed to execute query: {e}")

    def close(self) -> None:
        """Close the InfluxDB connection."""
        if self.client:
            self.client.close()


# Global database manager instance
db_manager = InfluxDBManager()
