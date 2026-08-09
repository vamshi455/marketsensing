/**
 * Main Dashboard Component — 6-panel layout
 *
 * Panels:
 * 1. Signals Overview — commodity list with BUY/SELL/NEUTRAL per contract
 * 2. Spread View — historical vs forecasted spreads with interactive date picker
 * 3. Market Signal Details — entry/exit dates, prices, margins, bid-ask impact
 * 4. Forecast Distribution — confidence intervals, Buy/Sell probability
 * 5. Feature Impact — waterfall chart of top N contributing features
 * 6. P&L Attribution — monthly MtM by product/strategy, cumulative total
 */

import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

import SignalsOverview from "../components/SignalsOverview";
import SpreadView from "../components/SpreadView";
import MarketSignalDetails from "../components/MarketSignalDetails";
import ForecastDistribution from "../components/ForecastDistribution";
import FeatureImpact from "../components/FeatureImpact";
import PnLAttribution from "../components/PnLAttribution";
import Filters from "../components/Filters";
import Navigation from "../components/Navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FilterState {
  commodity: string | null;
  spread: string | null;
  modelRunDate: string | null;
}

export default function Dashboard() {
  const [filters, setFilters] = useState<FilterState>({
    commodity: null,
    spread: null,
    modelRunDate: null,
  });

  const [activePanel, setActivePanel] = useState<"signals" | "backtesting">(
    "signals"
  );

  // Fetch signals based on filters
  const signalsQuery = useQuery({
    queryKey: ["signals", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.commodity) params.append("commodity", filters.commodity);
      if (filters.spread) params.append("spread", filters.spread);
      if (filters.modelRunDate) params.append("model_run_date", filters.modelRunDate);

      const response = await axios.get(`${API_BASE_URL}/signal-book`, { params });
      return response.data;
    },
    refetchInterval: 60000, // Refetch every minute
  });

  // Fetch spreads for selected commodity
  const spreadsQuery = useQuery({
    queryKey: ["spreads", filters.commodity],
    queryFn: async () => {
      if (!filters.commodity) return null;
      const response = await axios.get(
        `${API_BASE_URL}/spreads/${filters.commodity}`,
        { params: { days: 90 } }
      );
      return response.data;
    },
    enabled: !!filters.commodity,
  });

  // Fetch forecasts for selected commodity
  const forecastsQuery = useQuery({
    queryKey: ["forecasts", filters.commodity],
    queryFn: async () => {
      if (!filters.commodity) return null;
      const response = await axios.get(
        `${API_BASE_URL}/forecasts/${filters.commodity}`
      );
      return response.data;
    },
    enabled: !!filters.commodity,
  });

  // Fetch P&L attribution
  const pnlQuery = useQuery({
    queryKey: ["pnl", filters.commodity],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.commodity) params.append("commodity", filters.commodity);
      const response = await axios.get(`${API_BASE_URL}/pnl/attribution`, {
        params,
      });
      return response.data;
    },
    refetchInterval: 300000, // Refetch every 5 minutes
  });

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100">
      {/* Left Navigation Rail */}
      <Navigation activePanel={activePanel} onPanelChange={setActivePanel} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Filter Bar */}
        <Filters filters={filters} onFiltersChange={setFilters} />

        {/* Signal Summary Panel */}
        {activePanel === "signals" && (
          <div className="flex-1 overflow-auto p-4 space-y-4">
            {/* Row 1: Signals Overview + Spread View */}
            <div className="grid grid-cols-2 gap-4 h-1/2">
              <SignalsOverview
                signals={signalsQuery.data?.signals || []}
                isLoading={signalsQuery.isLoading}
              />
              <SpreadView
                spreads={spreadsQuery.data}
                commodity={filters.commodity}
                isLoading={spreadsQuery.isLoading}
              />
            </div>

            {/* Row 2: Market Signal Details + Forecast Distribution */}
            <div className="grid grid-cols-2 gap-4 h-1/2">
              <MarketSignalDetails
                signals={signalsQuery.data?.signals || []}
                isLoading={signalsQuery.isLoading}
              />
              <ForecastDistribution
                forecasts={forecastsQuery.data}
                commodity={filters.commodity}
                isLoading={forecastsQuery.isLoading}
              />
            </div>

            {/* Row 3: Feature Impact + P&L Attribution */}
            <div className="grid grid-cols-2 gap-4 h-1/2">
              <FeatureImpact
                commodity={filters.commodity}
                contract={null}
                isLoading={false}
              />
              <PnLAttribution
                pnlData={pnlQuery.data}
                isLoading={pnlQuery.isLoading}
              />
            </div>
          </div>
        )}

        {/* Backtesting Panel */}
        {activePanel === "backtesting" && (
          <div className="flex-1 overflow-auto p-4">
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-2xl font-bold mb-4">Backtesting Results</h2>
              <p className="text-slate-400">
                Backtest metrics for historical signal performance.
              </p>
              {/* TODO: Implement backtesting detail panel */}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
