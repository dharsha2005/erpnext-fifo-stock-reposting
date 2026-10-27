"""Manufacturing cost transfer for the simplified demo."""
from .models import D

def production_rate(input_cost, output_qty):
    """Allocate all consumed-material cost across produced quantity."""
    output_qty = D(output_qty)
    if output_qty <= 0:
        raise ValueError("Production quantity must be positive")
    return D(input_cost) / output_qty
