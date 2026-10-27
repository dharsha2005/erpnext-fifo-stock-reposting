import unittest
from decimal import Decimal as Dec
from fifo_reposting.models import Transaction
from fifo_reposting.reposting import calculate_valuations, repost_after_change, compare_valuations

def scenario(rate):
    w = "Main Warehouse"
    return [
        Transaction.make("OPEN", "2026-01-01", 1, "Milk", w, "receipt", 100, 50),
        Transaction.make("PR10", "2026-01-10", 1, "Milk", w, "receipt", 50, rate),
        Transaction.make("DN15", "2026-01-15", 1, "Milk", w, "issue", 80),
        Transaction.make("PR20", "2026-01-20", 1, "Milk", w, "receipt", 50, 60),
        Transaction.make("MFG21", "2026-01-21", 1, "Milk", w, "manufacture", 100,
                         output_item="Milk Powder", output_qty=10),
        Transaction.make("DN25", "2026-01-25", 1, "Milk Powder", w, "issue", 10),
    ]

class TestReposting(unittest.TestCase):
    def test_expected_before_after(self):
        before, after = repost_after_change(scenario(60), "PR10", 80)
        self.assertEqual(before["DN15"]["transaction_cost"], Dec("4000"))
        self.assertEqual(after["DN15"]["transaction_cost"], Dec("4000"))
        self.assertEqual(before["MFG21"]["production_cost"], Dec("5800"))
        self.assertEqual(after["MFG21"]["production_cost"], Dec("6800"))
        self.assertEqual(before["MFG21"]["output_rate"], Dec("580"))
        self.assertEqual(after["MFG21"]["output_rate"], Dec("680"))
        self.assertEqual(before["DN25"]["transaction_cost"], Dec("5800"))
        self.assertEqual(after["DN25"]["transaction_cost"], Dec("6800"))

    def test_report_and_idempotency(self):
        txs = scenario(60)
        original, changed = repost_after_change(txs, "PR10", 80)
        _, changed_again = repost_after_change(
            [Transaction.make(t.transaction_id, t.date, t.sequence, t.item,
                              t.warehouse, t.kind, t.qty,
                              80 if t.transaction_id == "PR10" else t.rate,
                              t.output_item, t.output_qty) for t in txs],
            "PR10", 80)
        self.assertEqual(changed, changed_again)
        report = {r["transaction_id"]: r for r in compare_valuations(original, changed)}
        self.assertFalse(report["DN15"]["affected"])
        self.assertTrue(report["MFG21"]["affected"])
        self.assertEqual(report["MFG21"]["difference"], Dec("1000"))

    def test_unknown_or_non_receipt_change(self):
        with self.assertRaises(KeyError):
            repost_after_change(scenario(60), "MISSING", 80)
        with self.assertRaises(ValueError):
            repost_after_change(scenario(60), "DN15", 80)

if __name__ == "__main__":
    unittest.main()
