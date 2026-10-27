from fifo_reposting.models import Transaction
from fifo_reposting.reposting import repost_after_change, compare_valuations

W = "Main Warehouse"
transactions = [
    Transaction.make("OPEN", "2026-01-01", 1, "Milk", W, "receipt", 100, 50),
    Transaction.make("PR10", "2026-01-10", 1, "Milk", W, "receipt", 50, 60),
    Transaction.make("DN15", "2026-01-15", 1, "Milk", W, "issue", 80),
    Transaction.make("PR20", "2026-01-20", 1, "Milk", W, "receipt", 50, 60),
    Transaction.make("MFG21", "2026-01-21", 1, "Milk", W, "manufacture", 100,
                     output_item="Milk Powder", output_qty=10),
    Transaction.make("DN25", "2026-01-25", 1, "Milk Powder", W, "issue", 10),
]

before, after = repost_after_change(transactions, "PR10", 80)
print("FIFO STOCK REPOSTING: BEFORE vs AFTER")
print(f"{'Transaction':<14} {'Item':<14} {'Old Cost':>12} {'New Cost':>12} {'Difference':>12}")
for row in compare_valuations(before, after):
    print(f"{row['transaction_id']:<14} {row['item']:<14} "
          f"₹{row['old_cost']:>10} ₹{row['new_cost']:>10} ₹{row['difference']:>10}")
print("\\nManufacturing: ₹5800 -> ₹6800")
print("Milk Powder valuation: ₹580/kg -> ₹680/kg")
print("Jan 15 issue stays ₹4000 because FIFO consumes opening stock first.")
