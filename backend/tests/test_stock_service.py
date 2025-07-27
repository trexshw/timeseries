"""Unit tests for stock data service."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.stock_service import StockDataService
from app.models.stock_data import StockDataPoint, TimeRangeQuery, StockDataResponse


class TestStockDataService:
    """Test cases for StockDataService."""

    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager."""
        mock_manager = Mock()
        mock_manager.write_point = Mock()
        mock_manager.write_points = Mock()
        mock_manager.query = Mock()
        return mock_manager

    @pytest.fixture
    def stock_service(self, mock_db_manager):
        """Create a stock service instance with mocked dependencies."""
        with patch('app.services.stock_service.db_manager', mock_db_manager):
            service = StockDataService()
            service.db_manager = mock_db_manager
            return service

    @pytest.fixture
    def sample_data_point(self):
        """Create a sample stock data point."""
        return StockDataPoint(
            symbol="AAPL",
            price=150.50,
            volume=1000,
            timestamp=datetime.utcnow()
        )

    @pytest.fixture
    def sample_time_range_query(self):
        """Create a sample time range query."""
        return TimeRangeQuery(
            symbol="AAPL",
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow(),
            interval="1m"
        )

    def test_store_data_point_success(self, stock_service, sample_data_point, mock_db_manager):
        """Test successful storage of a single data point."""
        # Act
        stock_service.store_data_point(sample_data_point)

        # Assert
        mock_db_manager.write_point.assert_called_once()
        call_args = mock_db_manager.write_point.call_args[0][0]
        assert call_args.get_tag("symbol") == "AAPL"
        assert call_args.get_field("price") == 150.50
        assert call_args.get_field("volume") == 1000

    def test_store_data_batch_success(self, stock_service, mock_db_manager):
        """Test successful storage of multiple data points."""
        # Arrange
        data_points = [
            StockDataPoint(symbol="AAPL", price=150.50, volume=1000),
            StockDataPoint(symbol="GOOGL", price=2500.00, volume=500)
        ]

        # Act
        stock_service.store_data_batch(data_points)

        # Assert
        mock_db_manager.write_points.assert_called_once()
        points = mock_db_manager.write_points.call_args[0][0]
        assert len(points) == 2
        assert points[0].get_tag("symbol") == "AAPL"
        assert points[1].get_tag("symbol") == "GOOGL"

    def test_query_data_by_time_range_success(self, stock_service, sample_time_range_query, mock_db_manager):
        """Test successful query of data by time range."""
        # Arrange
        mock_result = [
            Mock(
                records=[
                    Mock(
                        get_time=lambda: datetime.utcnow(),
                        get_value=lambda: 150.50,
                        values={"volume": 1000}
                    )
                ]
            )
        ]
        mock_db_manager.query.return_value = mock_result

        # Act
        result = stock_service.query_data_by_time_range(sample_time_range_query)

        # Assert
        assert isinstance(result, StockDataResponse)
        assert result.symbol == "AAPL"
        assert result.interval == "1m"
        assert len(result.data_points) == 1
        assert result.data_points[0]["price"] == 150.50

    def test_query_latest_data_success(self, stock_service, mock_db_manager):
        """Test successful query of latest data."""
        # Arrange
        symbol = "AAPL"
        mock_result = [
            Mock(
                records=[
                    Mock(
                        get_time=lambda: datetime.utcnow(),
                        get_value=lambda: 150.50,
                        values={"volume": 1000}
                    )
                ]
            )
        ]
        mock_db_manager.query.return_value = mock_result

        # Act
        result = stock_service.query_latest_data(symbol)

        # Assert
        assert isinstance(result, StockDataResponse)
        assert result.symbol == symbol
        assert len(result.data_points) == 1

    def test_get_available_symbols_success(self, stock_service, mock_db_manager):
        """Test successful retrieval of available symbols."""
        # Arrange
        mock_result = [
            Mock(
                records=[
                    Mock(values={"symbol": "AAPL"}),
                    Mock(values={"symbol": "GOOGL"}),
                    Mock(values={"symbol": "AAPL"})  # Duplicate
                ]
            )
        ]
        mock_db_manager.query.return_value = mock_result

        # Act
        symbols = stock_service.get_available_symbols()

        # Assert
        assert len(symbols) == 2
        assert "AAPL" in symbols
        assert "GOOGL" in symbols

    def test_store_data_point_database_error(self, stock_service, sample_data_point, mock_db_manager):
        """Test handling of database error when storing data point."""
        # Arrange
        mock_db_manager.write_point.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Failed to write point to InfluxDB"):
            stock_service.store_data_point(sample_data_point)

    def test_query_data_database_error(self, stock_service, sample_time_range_query, mock_db_manager):
        """Test handling of database error when querying data."""
        # Arrange
        mock_db_manager.query.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Failed to execute query"):
            stock_service.query_data_by_time_range(sample_time_range_query)

    def test_build_flux_query_with_times(self, stock_service, sample_time_range_query):
        """Test building Flux query with start and end times."""
        # Act
        query = stock_service._build_flux_query(sample_time_range_query)

        # Assert
        assert "AAPL" in query
        assert "1m" in query
        assert "aggregateWindow" in query

    def test_build_flux_query_without_times(self, stock_service):
        """Test building Flux query without start and end times."""
        # Arrange
        query_params = TimeRangeQuery(symbol="AAPL", interval="1h")

        # Act
        query = stock_service._build_flux_query(query_params)

        # Assert
        assert "AAPL" in query
        assert "1h" in query
        assert "aggregateWindow" in query

    def test_process_query_results_empty(self, stock_service):
        """Test processing empty query results."""
        # Act
        result = stock_service._process_query_results([])

        # Assert
        assert result == []

    def test_determine_time_range_with_times(self, stock_service, sample_time_range_query):
        """Test determining time range with provided times."""
        # Act
        time_range = stock_service._determine_time_range(sample_time_range_query)

        # Assert
        assert "start" in time_range
        assert "end" in time_range
        assert time_range["start"] == sample_time_range_query.start_time
        assert time_range["end"] == sample_time_range_query.end_time

    def test_determine_time_range_without_times(self, stock_service):
        """Test determining time range without provided times."""
        # Arrange
        query_params = TimeRangeQuery(symbol="AAPL", interval="1h")

        # Act
        time_range = stock_service._determine_time_range(query_params)

        # Assert
        assert "start" in time_range
        assert "end" in time_range
        assert time_range["start"] < time_range["end"]
