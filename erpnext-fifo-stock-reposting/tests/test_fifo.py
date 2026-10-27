import unittest
from decimal import Decimal as Dec
from fifo_reposting.fifo import FIFOStock

class TestFIFOStock(unittest.TestCase):
    def test_fifo_and_partial_layer(self):
        stock = FIFOStock()
        stock.receive(100, 50)
        stock.receive(50, 60)
        self.assertEqual(stock.issue(120), Dec("6200"))
        self.assertEqual(stock.quantity, Dec("30"))
        self.assertEqual(stock.value, Dec("1800"))

    def test_insufficient_stock(self):
        stock = FIFOStock()
        stock.receive(10, 50)
        with self.assertRaises(ValueError):
            stock.issue(11)

    def test_invalid_quantities_and_rate(self):
        stock = FIFOStock()
        for args in [(0, 50), (-1, 50), (1, -2)]:
            with self.assertRaises(ValueError):
                stock.receive(*args)
        with self.assertRaises(ValueError):
            stock.issue(0)

if __name__ == "__main__":
    unittest.main()
