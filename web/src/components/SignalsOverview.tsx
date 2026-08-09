/**
 * Panel 1: Signals Overview
 *
 * Displays:
 * - Table of commodities with their contracts and current predicted state
 * - Filtering by commodity
 * - Buy (green), Sell (red), Neutral (gray) indicators
 */

import React, { useMemo } from "react";
import { ChevronDownIcon, CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/solid";

interface Signal {
  signal_id: string;
  commodity: string;
  contract: string;
  predicted_state: "buy" | "sell" | "neutral";
  confidence: number;
  timestamp: string;
}

interface SignalsOverviewProps {
  signals: Signal[];
  isLoading: boolean;
}

const stateColors = {
  buy: "bg-green-500/10 text-green-400 border-green-500/20",
  sell: "bg-red-500/10 text-red-400 border-red-500/20",
  neutral: "bg-slate-500/10 text-slate-400 border-slate-500/20",
};

const stateBadges = {
  buy: "Long",
  sell: "Short",
  neutral: "Neutral",
};

export default function SignalsOverview({
  signals,
  isLoading,
}: SignalsOverviewProps) {
  // Group signals by commodity for easier viewing
  const groupedByComm = useMemo(() => {
    const groups: Record<string, Signal[]> = {};
    signals.forEach((s) => {
      if (!groups[s.commodity]) groups[s.commodity] = [];
      groups[s.commodity].push(s);
    });
    return groups;
  }, [signals]);

  if (isLoading) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 flex items-center justify-center">
        <div className="animate-spin">
          <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Signals Overview</h2>
        <span className="text-sm text-slate-400">
          {signals.length} active signals
        </span>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-slate-700/50">
            <tr className="border-b border-slate-600">
              <th className="px-4 py-2 text-left font-medium text-slate-300">
                Commodity
              </th>
              <th className="px-4 py-2 text-left font-medium text-slate-300">
                Contract
              </th>
              <th className="px-4 py-2 text-center font-medium text-slate-300">
                Predicted State
              </th>
              <th className="px-4 py-2 text-center font-medium text-slate-300">
                Confidence
              </th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(groupedByComm).length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-4 text-center text-slate-400">
                  No signals available
                </td>
              </tr>
            ) : (
              Object.entries(groupedByComm).map(([commodity, commSignals]) =>
                commSignals.map((signal, idx) => (
                  <tr
                    key={signal.signal_id}
                    className="border-b border-slate-700 hover:bg-slate-700/30 cursor-pointer"
                  >
                    {idx === 0 && (
                      <td
                        className="px-4 py-3 font-semibold text-blue-400"
                        rowSpan={commSignals.length}
                      >
                        {commodity}
                      </td>
                    )}
                    <td className="px-4 py-3">{signal.contract}</td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block px-3 py-1 rounded text-xs font-medium border ${
                          stateColors[signal.predicted_state]
                        }`}
                      >
                        {stateBadges[signal.predicted_state]}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-24 bg-slate-700 rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${
                              signal.predicted_state === "buy"
                                ? "bg-green-500"
                                : signal.predicted_state === "sell"
                                ? "bg-red-500"
                                : "bg-slate-500"
                            }`}
                            style={{
                              width: `${(signal.confidence || 0) * 100}%`,
                            }}
                          ></div>
                        </div>
                        <span className="text-xs text-slate-400 w-10">
                          {((signal.confidence || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))
              )
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-xs text-slate-500 border-t border-slate-700 pt-3">
        Model Run Date: {new Date().toISOString().split("T")[0]}
      </div>
    </div>
  );
}
