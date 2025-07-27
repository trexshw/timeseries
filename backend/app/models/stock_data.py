"""Pydantic models for stock trading data."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class StockDataPoint(BaseModel):
    """Model for a single stock data point."""

    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, GOOGL)")
    price: float = Field(..., gt=0, description="Stock price")
    volume: int = Field(..., ge=0, description="Trading volume")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data timestamp")

    @validator('symbol')
    def validate_symbol(cls, v: str) -> str:
        """Validate stock symbol format."""
        if not v.isalpha():
            raise ValueError('Symbol must contain only letters')
        return v.upper()

    @validator('price')
    def validate_price(cls, v: float) -> float:
        """Validate price is positive."""
        if v <= 0:
            raise ValueError('Price must be positive')
        return round(v, 2)

    @validator('volume')
    def validate_volume(cls, v: int) -> int:
        """Validate volume is non-negative."""
        if v < 0:
            raise ValueError('Volume must be non-negative')
        return v


class StockDataBatch(BaseModel):
    """Model for batch stock data points."""

    data_points: list[StockDataPoint] = Field(..., description="List of stock data points")

    @validator('data_points')
    def validate_data_points(cls, v: list[StockDataPoint]) -> list[StockDataPoint]:
        """Validate data points list is not empty."""
        if not v:
            raise ValueError('Data points list cannot be empty')
        return v


class TimeRangeQuery(BaseModel):
    """Model for time range queries."""

    symbol: str = Field(..., description="Stock symbol to query")
    start_time: Optional[datetime] = Field(None, description="Start time for query")
    end_time: Optional[datetime] = Field(None, description="End time for query")
    interval: str = Field(
        default="1m",
        description="Time interval (e.g., 1s, 1m, 1h, 1d)"
    )

    @validator('symbol')
    def validate_symbol(cls, v: str) -> str:
        """Validate stock symbol format."""
        if not v.isalpha():
            raise ValueError('Symbol must contain only letters')
        return v.upper()

    @validator('interval')
    def validate_interval(cls, v: str) -> str:
        """Validate time interval format."""
        valid_intervals = ['1s', '5s', '10s', '30s', '1m', '5m', '15m', '30m', '1h', '4h', '1d']
        if v not in valid_intervals:
            raise ValueError(f'Interval must be one of: {valid_intervals}')
        return v


class StockDataResponse(BaseModel):
    """Model for stock data query response."""

    symbol: str
    data_points: list[dict]
    total_points: int
    time_range: dict[str, datetime]
    interval: str


class HealthResponse(BaseModel):
    """Model for health check response."""

    status: str
    timestamp: datetime
    database_connected: bool
    version: str
