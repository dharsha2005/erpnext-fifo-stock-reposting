"""FIFO inventory layers and issue-cost calculation."""
from collections import deque
from decimal import Decimal
from .models import D

class FIFOStock:
    """An in-memory FIFO stock queue for one item/warehouse."""
    def __init__(self):
        self.layers = deque()

    @property
    def quantity(self):
        return sum((layer[0] for layer in self.layers), D(0))

    @property
    def value(self):
        return sum((qty * rate for qty, rate in self.layers), D(0))

    def receive(self, qty, rate):
        qty, rate = D(qty), D(rate)
        if qty <= 0:
            raise ValueError("Receipt quantity must be positive")
        if rate < 0:
            raise ValueError("Receipt rate cannot be negative")
        self.layers.append([qty, rate])

    def issue(self, qty):
        qty = D(qty)
        if qty <= 0:
            raise ValueError("Issue quantity must be positive")
        if qty > self.quantity:
            raise ValueError(
                f"Insufficient stock: requested {qty}, available {self.quantity}"
            )
        remaining, cost = qty, D(0)
        while remaining > 0:
            layer_qty, rate = self.layers[0]
            taken = min(remaining, layer_qty)
            cost += taken * rate
            remaining -= taken
            layer_qty -= taken
            if layer_qty == 0:
                self.layers.popleft()
            else:
                self.layers[0][0] = layer_qty
        return cost
