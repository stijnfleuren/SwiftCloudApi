from typing import Dict


class KPIs:
    def __init__(self, delay: float, capacity: float):
        """
        :param delay: estimation of the the delay (in seconds) that road users are expected to experience at the
        intersection.
        :param capacity: the largest increase in traffic that the intersection is expected to be able to handle.
        For example, capacity=1.1 would indicate that the intersection can handle a 10% increase in traffic, while
        capacity=0.9 indicates that the intersection is already oversaturated (and this amount of traffic has to reduce
        by 10% for the intersection to become 'stable' again).
        """
        self.delay = delay
        self.capacity = capacity

    def to_json(self):
        return {"delay": self.delay, "capacity": self.capacity}

    @classmethod
    def from_json(cls, json_dict: Dict[str, float]):
        return cls(**json_dict)

    def __repr__(self):
        return f"KPIs: delay={self.delay:.2f}s, capacity={self.capacity:.3f}"
