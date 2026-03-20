# Runbook: EIA Crude Inventory Report Day

## Schedule
Every Wednesday at 10:30am ET

## Pre-Report (T-30 min)
1. Verify market data feeds are healthy
2. Confirm kill-switch is armed for affected strategies
3. Check consensus forecast is loaded in `silver.eia_inventory`

## At Release (T+0)
1. Kill-switch mutes signals for 10 minutes post-release
2. Batch pipeline ingests EIA data via ADF
3. `inventory_surprise` feature is computed (actual - forecast)

## Post-Report (T+15 min)
1. Kill-switch lifts, signals resume
2. Verify `gold.fundamental_features` updated with new inventory data
3. Check signal log for any new signals triggered by inventory surprise

## Troubleshooting
- **No EIA data after T+5 min**: Check ADF pipeline status, verify EIA API is responding
- **Kill-switch not lifting**: Check `config/risk_limits.yaml` kill-switch settings
- **Stale features**: Verify feature computation job ran post-ingestion
