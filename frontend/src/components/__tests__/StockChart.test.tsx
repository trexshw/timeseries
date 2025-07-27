import React from "react";
import { render, screen } from "@testing-library/react";
import StockChart from "../StockChart";
import { ChartDataPoint } from "../../types/stock";

const mockData: ChartDataPoint[] = [
  {
    timestamp: "2023-12-01T10:00:00Z",
    price: 150.5,
    volume: 1000,
  },
  {
    timestamp: "2023-12-01T10:01:00Z",
    price: 151.0,
    volume: 1200,
  },
];

describe("StockChart", () => {
  it("renders chart with data", () => {
    render(
      <StockChart
        data={mockData}
        symbol="AAPL"
        height={400}
        showVolume={false}
      />
    );

    expect(screen.getByText("AAPL Stock Chart")).toBeInTheDocument();
    expect(screen.getByText("2 data points")).toBeInTheDocument();
  });

  it("renders empty state when no data", () => {
    render(
      <StockChart data={[]} symbol="AAPL" height={400} showVolume={false} />
    );

    expect(screen.getByText("No data available for AAPL")).toBeInTheDocument();
  });

  it("renders with volume chart when showVolume is true", () => {
    render(
      <StockChart
        data={mockData}
        symbol="AAPL"
        height={400}
        showVolume={true}
      />
    );

    expect(screen.getByText("AAPL Stock Chart")).toBeInTheDocument();
  });
});
