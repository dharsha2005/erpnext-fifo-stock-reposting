import unittest
from decimal import Decimal as Dec
from fifo_reposting.manufacturing import production_rate

class TestManufacturing(unittest.TestCase):
    def test_cost_transfers_to_output(self):
        self.assertEqual(production_rate(5800, 10), Dec("580"))
        self.assertEqual(production_rate(6800, 10), Dec("680"))

    def test_invalid_output_quantity(self):
        with self.assertRaises(ValueError):
            production_rate(100, 0)

if __name__ == "__main__":
    unittest.main()
