"""Deterministic transaction replay and before/after comparison."""
from collections import defaultdict
from decimal import Decimal
from .fifo import FIFOStock
from .models import D
from .manufacturing import production_rate

def ordered(transactions):
    """Stable chronological ordering: date, sequence, transaction ID."""
    return sorted(transactions, key=lambda t: (t.date, t.sequence, t.transaction_id))

def calculate_valuations(transactions):
    """
    Replay transactions from the beginning and return per-transaction results.

    A manufacture transaction issues its input item and receives its output item
    at the consumed-material cost per output unit. Other production costs,
    taxes, returns, and negative stock are outside this demo's scope.
    """
    stocks = defaultdict(FIFOStock)
    results = {}
    for tx in ordered(transactions):
        key = (tx.item, tx.warehouse)
        stock = stocks[key]
        if tx.kind == "receipt":
            if tx.rate is None:
                raise ValueError(f"{tx.transaction_id}: receipt requires a rate")
            stock.receive(tx.qty, tx.rate)
            cost = tx.qty * tx.rate
        elif tx.kind in ("issue", "manufacture"):
            cost = stock.issue(tx.qty)
        else:
            raise ValueError(f"{tx.transaction_id}: unsupported kind {tx.kind}")

        result = {
            "transaction_id": tx.transaction_id,
            "item": tx.item,
            "kind": tx.kind,
            "qty": tx.qty,
            "transaction_cost": cost,
            "stock_qty_after": stock.quantity,
            "stock_value_after": stock.value,
        }
        results[tx.transaction_id] = result

        if tx.kind == "manufacture":
            if not tx.output_item or tx.output_qty is None:
                raise ValueError(f"{tx.transaction_id}: missing manufacturing output")
            output_stock = stocks[(tx.output_item, tx.warehouse)]
            rate = production_rate(cost, tx.output_qty)
            output_stock.receive(tx.output_qty, rate)
            results[tx.transaction_id]["production_cost"] = cost
            results[tx.transaction_id]["output_rate"] = rate
            results[tx.transaction_id]["output_item"] = tx.output_item
            results[tx.transaction_id]["output_qty"] = tx.output_qty
            results[tx.transaction_id]["output_stock_qty_after"] = output_stock.quantity
            results[tx.transaction_id]["output_stock_value_after"] = output_stock.value

    return results

def repost_after_change(transactions, transaction_id, new_rate):
    """Return original and replayed valuations after changing a receipt rate."""
    found = False
    changed = []
    new_rate = D(new_rate)
    for tx in transactions:
        if tx.transaction_id == transaction_id:
            found = True
            if tx.kind != "receipt":
                raise ValueError("Only receipt rates can be changed")
            changed.append(type(tx)(
                transaction_id=tx.transaction_id, date=tx.date,
                sequence=tx.sequence, item=tx.item, warehouse=tx.warehouse,
                kind=tx.kind, qty=tx.qty, rate=new_rate,
                output_item=tx.output_item, output_qty=tx.output_qty
            ))
        else:
            changed.append(tx)
    if not found:
        raise KeyError(f"Unknown transaction: {transaction_id}")
    return calculate_valuations(transactions), calculate_valuations(changed)

def compare_valuations(before, after):
    """Report transaction cost changes and final output valuation changes."""
    report = []
    for txid in before:
        old, new = before[txid], after[txid]
        old_cost = old["transaction_cost"]
        new_cost = new["transaction_cost"]
        changed = old_cost != new_cost
        row = {
            "transaction_id": txid,
            "item": old["item"],
            "old_cost": old_cost,
            "new_cost": new_cost,
            "difference": new_cost - old_cost,
            "affected": changed,
        }
        if "production_cost" in old:
            row["old_production_cost"] = old["production_cost"]
            row["new_production_cost"] = new["production_cost"]
            row["old_output_rate"] = old["output_rate"]
            row["new_output_rate"] = new["output_rate"]
        report.append(row)
    return report
