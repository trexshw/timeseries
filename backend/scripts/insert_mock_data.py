#!/usr/bin/env python3
"""
Script to insert mock stock data into InfluxDB for testing and development.

This script generates realistic stock data with:
- Multiple stock symbols (AAPL, GOOGL, MSFT, TSLA, AMZN)
- Realistic price movements with volatility
- Volume data
- Timestamp data over the last 30 days
"""

import os
import sys
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from influxdb_client import InfluxDBClient, Point
from app.core.config import settings


class MockDataGenerator:
    """Generate realistic mock stock data."""

    def __init__(self):
        """Initialize the mock data generator."""
        self.symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        self.base_prices = {
            "AAPL": 150.0,
            "GOOGL": 2800.0,
            "MSFT": 300.0,
            "TSLA": 800.0,
            "AMZN": 3300.0
        }
        self.volatility = {
            "AAPL": 0.02,
            "GOOGL": 0.025,
            "MSFT": 0.018,
            "TSLA": 0.04,
            "AMZN": 0.03
        }

    def generate_price_movement(self, symbol: str, current_price: float) -> float:
        """Generate realistic price movement using random walk with volatility."""
        volatility = self.volatility[symbol]
        # Random walk with mean reversion
        change_percent = random.gauss(0, volatility)
        # Add some mean reversion to keep prices reasonable
        if current_price > self.base_prices[symbol] * 1.2:
            change_percent -= 0.01
        elif current_price < self.base_prices[symbol] * 0.8:
            change_percent += 0.01

        new_price = current_price * (1 + change_percent)
        return max(new_price, 1.0)  # Ensure price doesn't go below $1

    def generate_volume(self, symbol: str, base_volume: int = 1000000) -> int:
        """Generate realistic volume data."""
        # Volume varies by symbol and has some randomness
        volume_multipliers = {
            "AAPL": 1.5,
            "GOOGL": 0.8,
            "MSFT": 1.2,
            "TSLA": 2.0,
            "AMZN": 1.0
        }

        multiplier = volume_multipliers[symbol]
        # Add some randomness to volume
        random_factor = random.uniform(0.5, 1.5)
        volume = int(base_volume * multiplier * random_factor)
        return max(volume, 1000)  # Ensure minimum volume

    def generate_data_points(self, days: int = 30, interval_minutes: int = 15) -> List[Point]:
        """Generate mock data points for all symbols over the specified period."""
        points = []
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        # Generate data for each symbol
        for symbol in self.symbols:
            current_price = self.base_prices[symbol]
            current_time = start_time

            print(f"Generating data for {symbol}...")

            while current_time <= end_time:
                # Generate price movement
                current_price = self.generate_price_movement(symbol, current_price)

                # Generate volume
                volume = self.generate_volume(symbol)

                # Create InfluxDB point
                point = Point("stock_data") \
                    .tag("symbol", symbol) \
                    .field("price", current_price) \
                    .field("volume", volume) \
                    .time(current_time)

                points.append(point)

                # Move to next interval
                current_time += timedelta(minutes=interval_minutes)

                # Add some market hours logic (9:30 AM - 4:00 PM EST, weekdays only)
                if current_time.hour < 9 or current_time.hour >= 16 or current_time.weekday() >= 5:
                    # Outside market hours, skip or reduce data frequency
                    current_time += timedelta(hours=16)  # Skip to next market day

                # Progress indicator
                if len(points) % 1000 == 0:
                    print(f"  Generated {len(points)} points so far...")

        return points


def main():
    """Main function to insert mock data."""
    print("🚀 Starting Mock Data Insertion...")
    print("=" * 50)

    try:
        # Initialize InfluxDB client
        print("📡 Connecting to InfluxDB...")
        client = InfluxDBClient(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org
        )

        # Test connection
        health = client.health()
        if health.status != "pass":
            raise ConnectionError(f"InfluxDB health check failed: {health.message}")

        print("✅ Successfully connected to InfluxDB")

        # Initialize write API
        write_api = client.write_api()

        # Generate mock data
        print("📊 Generating mock data...")
        generator = MockDataGenerator()
        data_points = generator.generate_data_points(days=30, interval_minutes=15)

        print(f"📈 Generated {len(data_points)} data points")
        print(f"📅 Time range: Last 30 days")
        print(f"🕐 Interval: 15 minutes")
        print(f"📊 Symbols: {', '.join(generator.symbols)}")

        # Write data to InfluxDB
        print("💾 Writing data to InfluxDB...")
        start_time = time.time()

        # Write in batches to avoid memory issues
        batch_size = 1000
        for i in range(0, len(data_points), batch_size):
            batch = data_points[i:i + batch_size]
            write_api.write(
                bucket=settings.influxdb_bucket,
                record=batch
            )
            print(f"  Written batch {i//batch_size + 1}/{(len(data_points) + batch_size - 1)//batch_size}")

        write_api.close()

        end_time = time.time()
        print(f"✅ Successfully inserted {len(data_points)} data points in {end_time - start_time:.2f} seconds")

        # Verify data insertion
        print("🔍 Verifying data insertion...")
        query_api = client.query_api()

        # Check total points per symbol
        for symbol in generator.symbols:
            query = f'''
            from(bucket: "{settings.influxdb_bucket}")
                |> range(start: -30d)
                |> filter(fn: (r) => r["_measurement"] == "stock_data")
                |> filter(fn: (r) => r["symbol"] == "{symbol}")
                |> count()
            '''

            result = query_api.query(query=query, org=settings.influxdb_org)
            count = 0
            for table in result:
                for record in table.records:
                    count = record.get_value()

            print(f"  {symbol}: {count} data points")

        # Get latest prices
        print("\n📊 Latest prices:")
        for symbol in generator.symbols:
            query = f'''
            from(bucket: "{settings.influxdb_bucket}")
                |> range(start: -1h)
                |> filter(fn: (r) => r["_measurement"] == "stock_data")
                |> filter(fn: (r) => r["symbol"] == "{symbol}")
                |> filter(fn: (r) => r["_field"] == "price")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''

            result = query_api.query(query=query, org=settings.influxdb_org)
            for table in result:
                for record in table.records:
                    price = record.get_value()
                    print(f"  {symbol}: ${price:.2f}")

        client.close()
        print("\n🎉 Mock data insertion completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
