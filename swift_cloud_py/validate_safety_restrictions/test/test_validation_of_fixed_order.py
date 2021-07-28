import unittest
from collections import defaultdict
from itertools import combinations
from typing import List

from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.periodic_order import PeriodicOrder
from swift_cloud_py.entities.intersection.sg_relations import Conflict
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight
from swift_cloud_py.validate_safety_restrictions.validate_fixed_orders import validate_fixed_orders


class TestValidatingCompleteness(unittest.TestCase):
    """ Unittests of the function find_other_sg_relation_matches """

    def setUp(self) -> None:
        self._signal_groups = []
        self._fixed_orders = []
        self._greenyellow_intervals = defaultdict(list)
        self._period = None

    def test_three_signalgroups_valid(self):
        self._add_signalgroup(name="sg1")
        self._add_signalgroup(name="sg2")
        self._add_signalgroup(name="sg3")
        self._add_greenyellow_interval(name="sg1", start=2, end=10)
        self._add_greenyellow_interval(name="sg2", start=12, end=20)
        self._add_greenyellow_interval(name="sg3", start=22, end=30)
        self._add_fixed_periodic_order(order=["sg1", "sg2", "sg3"])
        self._set_period(period=40)
        self._expect_valid_fixed_order()

    def test_three_signalgroups_not_valid(self):
        self._add_signalgroup(name="sg1")
        self._add_signalgroup(name="sg2")
        self._add_signalgroup(name="sg3")
        self._add_greenyellow_interval(name="sg1", start=2, end=10)
        self._add_greenyellow_interval(name="sg2", start=12, end=20)
        self._add_greenyellow_interval(name="sg3", start=22, end=30)
        self._add_fixed_periodic_order(order=["sg1", "sg3", "sg2"])
        self._set_period(period=40)
        self._expect_valid_fixed_order(expect_valid=False)

    def test_shift_invariance_valid(self) -> None:
        self._add_signalgroup(name="sg1")
        self._add_signalgroup(name="sg2")
        self._add_signalgroup(name="sg3")
        self._set_period(period=40)
        self._add_greenyellow_interval(name="sg1", start=2, end=10)
        self._add_greenyellow_interval(name="sg2", start=12, end=20)
        self._add_greenyellow_interval(name="sg3", start=22, end=30)
        self._add_fixed_periodic_order(order=["sg1", "sg2", "sg3"])

        for shift in [shift for shift in range(0, 50, 1)]:
            with self.subTest(f"shift={shift}"):
                self._expect_valid_fixed_order(shift=shift)

    def test_shift_invariance_not_valid(self) -> None:
        self._add_signalgroup(name="sg1")
        self._add_signalgroup(name="sg2")
        self._add_signalgroup(name="sg3")
        self._add_greenyellow_interval(name="sg1", start=2, end=10)
        self._add_greenyellow_interval(name="sg2", start=12, end=20)
        self._add_greenyellow_interval(name="sg3", start=22, end=30)
        self._add_fixed_periodic_order(order=["sg1", "sg3", "sg2"])
        self._set_period(period=40)

        for shift in [shift for shift in range(0, 50, 1)]:
            with self.subTest(f"shift={shift}"):
                self._expect_valid_fixed_order(shift=shift, expect_valid=False)

    def test_four_signalgroups_valid(self):
        self._add_signalgroup(name="sg1")
        self._add_signalgroup(name="sg2")
        self._add_signalgroup(name="sg3")
        self._add_signalgroup(name="sg4")
        self._add_greenyellow_interval(name="sg1", start=2, end=10)
        self._add_greenyellow_interval(name="sg2", start=12, end=20)
        self._add_greenyellow_interval(name="sg3", start=22, end=30)
        self._add_greenyellow_interval(name="sg4", start=32, end=40)
        self._add_fixed_periodic_order(order=["sg1", "sg2", "sg3"])
        self._add_fixed_periodic_order(order=["sg1", "sg3", "sg4"])
        self._set_period(period=50)

        for shift in [shift for shift in range(0, 60, 1)]:
            with self.subTest(f"shift={shift}"):
                self._expect_valid_fixed_order(shift=shift)

    def test_four_signalgroups_invalid(self):
        self._add_signalgroup(name="sg1")
        self._add_signalgroup(name="sg2")
        self._add_signalgroup(name="sg3")
        self._add_signalgroup(name="sg4")
        self._add_greenyellow_interval(name="sg1", start=2, end=10)
        self._add_greenyellow_interval(name="sg2", start=12, end=20)
        self._add_greenyellow_interval(name="sg3", start=22, end=30)
        self._add_greenyellow_interval(name="sg4", start=32, end=40)
        self._add_fixed_periodic_order(order=["sg1", "sg2", "sg3"])
        self._add_fixed_periodic_order(order=["sg1", "sg4", "sg3"])
        self._set_period(period=50)

        for shift in [shift for shift in range(0, 60, 1)]:
            with self.subTest(f"shift={shift}"):
                self._expect_valid_fixed_order(shift=shift, expect_valid=False)

    def test_multiple_greenyellow_intervals_valid(self):
        self._add_signalgroup(name="sg1")
        self._add_signalgroup(name="sg2")
        self._add_signalgroup(name="sg3")
        self._add_greenyellow_interval(name="sg1", start=2, end=10)
        self._add_greenyellow_interval(name="sg1", start=12, end=20)
        self._add_greenyellow_interval(name="sg2", start=22, end=30)
        self._add_greenyellow_interval(name="sg2", start=32, end=40)
        self._add_greenyellow_interval(name="sg3", start=42, end=50)
        self._add_greenyellow_interval(name="sg3", start=52, end=60)
        self._add_fixed_periodic_order(order=["sg1", "sg2", "sg3"])
        self._set_period(period=70)
        self._expect_valid_fixed_order()

    def test_multiple_greenyellow_intervals_not_valid(self):
        self._add_signalgroup(name="sg1")
        self._add_signalgroup(name="sg2")
        self._add_signalgroup(name="sg3")
        self._add_greenyellow_interval(name="sg1", start=2, end=10)
        self._add_greenyellow_interval(name="sg3", start=12, end=20)
        self._add_greenyellow_interval(name="sg2", start=22, end=30)
        self._add_greenyellow_interval(name="sg2", start=32, end=40)
        self._add_greenyellow_interval(name="sg3", start=42, end=50)
        self._add_greenyellow_interval(name="sg1", start=52, end=60)
        self._add_fixed_periodic_order(order=["sg1", "sg2", "sg3"])
        self._set_period(period=70)
        self._expect_valid_fixed_order(expect_valid=False)

    def _add_greenyellow_interval(self, name: str, start: float, end: float) -> None:
        self._greenyellow_intervals[name].append([start, end])

    def _add_fixed_periodic_order(self, order: List[str]) -> None:
        self._fixed_orders.append(PeriodicOrder(order=order))

    def _set_period(self, period: float) -> None:
        self._period = period

    def _add_signalgroup(self, name: str) -> None:
        traffic_light = TrafficLight(capacity=0.5, lost_time=0.0)
        self._signal_groups.append(SignalGroup(id=name, traffic_lights=[traffic_light],
                                               min_greenyellow=2, max_greenyellow=20, min_red=2,
                                               max_red=50, min_nr=1, max_nr=3))

    def _expect_valid_fixed_order(self, expect_valid: bool = True, shift: float = 0) -> None:
        # assume all signalgroups are conflicting for this test
        conflicts = []
        for signalgroup1, signalgroup2 in combinations(self._signal_groups, 2):
            if signalgroup1 == signalgroup2:
                continue
            conflicts.append(Conflict(id1=signalgroup1.id, id2=signalgroup2.id, setup12=1, setup21=1))
        intersection = Intersection(signalgroups=self._signal_groups, conflicts=conflicts,
                                    periodic_orders=self._fixed_orders)

        fts_dict = {"period": self._period,
                    "greenyellow_intervals": {name: [[(t + shift) % self._period for t in interval]
                                                     for interval in intervals]
                                              for name, intervals in self._greenyellow_intervals.items()}}

        fts = FixedTimeSchedule.from_json(fts_dict=fts_dict)
        valid = True
        try:
            validate_fixed_orders(intersection=intersection, fts=fts)
        except SafetyViolation:
            valid = False

        self.assertEqual(valid, expect_valid)
