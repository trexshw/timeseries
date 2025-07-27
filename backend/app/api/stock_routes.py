"""API routes for stock data operations."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.stock_data import (
    StockDataPoint,
    StockDataBatch,
    TimeRangeQuery,
    StockDataResponse
)
from app.services.stock_service import stock_service

router = APIRouter(prefix="/api/v1/stocks", tags=["stocks"])


@router.post("/data", response_model=dict, status_code=status.HTTP_201_CREATED)
async def store_stock_data(data_point: StockDataPoint) -> dict:
    """Store a single stock data point."""
    try:
        stock_service.store_data_point(data_point)
        return {
            "message": "Data point stored successfully",
            "symbol": data_point.symbol,
            "timestamp": data_point.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store data point: {str(e)}"
        )


@router.post("/data/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def store_stock_data_batch(data_batch: StockDataBatch) -> dict:
    """Store multiple stock data points."""
    try:
        stock_service.store_data_batch(data_batch.data_points)
        return {
            "message": "Data batch stored successfully",
            "count": len(data_batch.data_points),
            "symbols": list(set(dp.symbol for dp in data_batch.data_points))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store data batch: {str(e)}"
        )


@router.post("/query", response_model=StockDataResponse)
async def query_stock_data(query: TimeRangeQuery) -> StockDataResponse:
    """Query stock data within a specified time range."""
    try:
        return stock_service.query_data_by_time_range(query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query data: {str(e)}"
        )


@router.get("/{symbol}/latest", response_model=StockDataResponse)
async def get_latest_stock_data(symbol: str, limit: int = 100) -> StockDataResponse:
    """Get the latest stock data for a specific symbol."""
    try:
        return stock_service.query_latest_data(symbol, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest data: {str(e)}"
        )


@router.get("/symbols", response_model=List[str])
async def get_available_symbols() -> List[str]:
    """Get list of available stock symbols."""
    try:
        return stock_service.get_available_symbols()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get symbols: {str(e)}"
        )


@router.get("/health", response_model=dict)
async def health_check() -> dict:
    """Health check endpoint for stock service."""
    try:
        # Test database connection
        symbols = stock_service.get_available_symbols()
        return {
            "status": "healthy",
            "database_connected": True,
            "available_symbols_count": len(symbols)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e)
        }
