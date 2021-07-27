from __future__ import annotations

from copy import deepcopy
from typing import List, Dict


class PeriodicOrder:
    def __init__(self, order: List[str]):
        """ Order in which to serve signal groups"""
        self._order = order

        # validate values of arguments
        self._validate()

    def __repr__(self) -> str:
        return f"FixedOrder({self._order})"

    @property
    def order(self) -> List[str]:
        return self._order

    def __iter__(self):
        return iter(self._order)

    @classmethod
    def from_json(cls, order_dict: Dict) -> PeriodicOrder:
        return cls(order=order_dict["order"])

    def to_json(self) -> Dict:
        return {"order": deepcopy(self._order)}

    def _validate(self):
        """ Validate input arguments of Confict """
        if len(set(self._order)) != len(self._order):
            raise ValueError("Items in 'order' should be unique")
