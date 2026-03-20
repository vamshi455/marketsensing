# ADR-003: Signal-Only Architecture in v1

## Status
Accepted

## Context
The platform could be designed end-to-end with execution capabilities, but this increases complexity, regulatory risk, and time to market.

## Decision
v1 is **signal-only**: the system produces ranked trade ideas (Signal Book) but does not place orders. The architecture must support adding an order-management/execution layer later.

## Consequences
- Faster time to market — focus on signal quality first
- Clean API boundary between signals and execution
- Traders review and act on signals manually in v1
- Signal schema includes fields (size, confidence, hold time) that the execution layer will consume
- No need for FIX connectivity or order state management in v1
