#!/usr/bin/env python3
"""Setup script for initializing the stock trading data system."""

import asyncio
import random
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "admin-token-123"
INFLUXDB_ORG = "timeseries"
INFLUXDB_BUCKET = "stock_data"

# Sample stock symbols
STOCK_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"]

def create_sample_data():
    """Create sample stock data for testing."""
    client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Generate data for the last 7 days
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    points = []

    for symbol in STOCK_SYMBOLS:
        # Generate random starting price between 50 and 500
        base_price = random.uniform(50, 500)

        current_time = start_time
        while current_time <= end_time:
            # Add some randomness to the price
            price_change = random.uniform(-5, 5)
            price = max(1, base_price + price_change)
            base_price = price

            # Generate random volume
            volume = random.randint(1000, 10000)

            point = Point("stock_data") \
                .tag("symbol", symbol) \
                .field("price", round(price, 2)) \
                .field("volume", volume) \
                .time(current_time)

            points.append(point)

            # Move to next minute
            current_time += timedelta(minutes=1)

    print(f"Writing {len(points)} data points to InfluxDB...")
    write_api.write(bucket=INFLUXDB_BUCKET, record=points)
    print("Sample data created successfully!")

    client.close()

def check_connection():
    """Check if InfluxDB is accessible."""
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )

        # Test connection by querying buckets
        buckets_api = client.buckets_api()
        buckets = buckets_api.find_buckets()

        print("✅ Successfully connected to InfluxDB")
        print(f"Found {len(buckets)} buckets")

        # Check if our bucket exists
        bucket_names = [bucket.name for bucket in buckets]
        if INFLUXDB_BUCKET in bucket_names:
            print(f"✅ Bucket '{INFLUXDB_BUCKET}' exists")
        else:
            print(f"❌ Bucket '{INFLUXDB_BUCKET}' not found")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Failed to connect to InfluxDB: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Stock Trading Data System...")
    print("=" * 50)

    # Check connection
    if not check_connection():
        print("Please make sure InfluxDB is running and accessible")
        return

    # Create sample data
    print("\n📊 Creating sample data...")
    create_sample_data()

    print("\n✅ Setup completed successfully!")
    print("\nYou can now:")
    print("1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Access the API docs: http://localhost:8000/docs")
    print("4. Access the frontend: http://localhost:3000")

if __name__ == "__main__":
    main()
