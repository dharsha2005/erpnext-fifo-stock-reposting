"""Simple transaction models for the FIFO reposting demonstration."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

def D(value):
    """Convert values to Decimal without introducing binary float errors."""
    return Decimal(str(value))

@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    date: str
    sequence: int
    item: str
    warehouse: str
    kind: str  # receipt, issue, manufacture
    qty: Decimal
    rate: Optional[Decimal] = None
    output_item: Optional[str] = None
    output_qty: Optional[Decimal] = None

    @classmethod
    def make(cls, transaction_id, date, sequence, item, warehouse, kind,
             qty, rate=None, output_item=None, output_qty=None):
        return cls(
            transaction_id=transaction_id,
            date=date,
            sequence=sequence,
            item=item,
            warehouse=warehouse,
            kind=kind,
            qty=D(qty),
            rate=None if rate is None else D(rate),
            output_item=output_item,
            output_qty=None if output_qty is None else D(output_qty),
        )
