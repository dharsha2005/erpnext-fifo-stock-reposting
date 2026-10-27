# ERPNext FIFO Stock Reposting Demo

## Objective
This standalone Python project demonstrates how changing a historical Milk Purchase Receipt rate from ₹60/L to ₹80/L affects later FIFO valuation and manufacturing cost.

**This is a simulation, not an ERPNext integration.** It does not write Stock Ledger Entries or General Ledger entries.

## Approach and design decisions
- **FIFO layers:** each receipt adds a quantity/rate layer; issues consume the oldest layer first.
- **Decimal:** `Decimal` avoids binary floating-point rounding errors in financial calculations.
- **Deterministic replay:** transactions are sorted by posting date, sequence, and transaction ID.
- **Replay from source transactions:** instead of trusting stored running balances, the engine rebuilds valuations from the transaction history.
- **Manufacturing dependency:** the consumed Milk issue cost becomes the cost of the produced Milk Powder in this simplified scenario.
- **Separation of concerns:** models, FIFO operations, manufacturing cost allocation, and reposting are separate modules.
- **Repeatability:** replaying the same source transactions produces the same results.

## Example results

| Transaction | Before | After |
|---|---:|---:|
| Jan 15 Milk issue | ₹4,000 | ₹4,000 |
| Jan 21 manufacturing cost | ₹5,800 | ₹6,800 |
| Milk Powder rate | ₹580/kg | ₹680/kg |
| Jan 25 Powder issue | ₹5,800 | ₹6,800 |

The January 15 issue is unchanged because the 80 L issue consumes 80 L from the opening layer of 100 L at ₹50/L. The rate change affects the remaining January 10 layer, which is consumed during manufacturing.

## Run
Python 3.11 or newer is recommended. No third-party packages are required.

```bash
python -m unittest discover -v
python examples/scenario.py
```

Run the example from the project root. If your environment does not add the root to Python's import path, use:

```bash
python -m examples.scenario
```

## Running balance risks
If a system persists a running quantity/value on every ledger row, a backdated receipt edit can make later balances stale. Reports may then disagree with FIFO layers, issue costs, manufacturing valuation, or accounting. Replaying affected transactions from source events is one way to rebuild consistent derived values.

## Limitations
- In-memory educational prototype only; no database, locks, concurrent job handling, audit log, returns, cancellations, taxes, freight, or additional manufacturing costs.
- Manufacturing allocates consumed-material cost equally across output quantity and assumes one output item.
- The reposting function replays the full supplied history for clarity; production systems may optimize by replaying from a safe checkpoint.
- This does not replace ERPNext's supported Repost Item Valuation or accounting reposting workflow. Production integration must use version-compatible ERPNext APIs and reconcile stock and GL values safely.
