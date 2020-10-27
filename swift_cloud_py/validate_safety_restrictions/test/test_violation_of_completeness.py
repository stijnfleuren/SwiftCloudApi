import unittest
from typing import List, Optional

from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule, GreenYellowInterval
from swift_cloud_py.entities.intersection.sg_relations import Conflict
from swift_cloud_py.validate_safety_restrictions.validate_completeness import validate_completeness


class TestValidatingCompleteness(unittest.TestCase):
    """ Unittests of the function find_other_sg_relation_matches """

    @staticmethod
    def get_default_signalgroup(name: str, min_greenyellow: float = 10.0, max_greenyellow: float = 80.0,
                                min_red: float = 10.0, max_red: float = 80.0) -> SignalGroup:
        """ Get a default signalgroup object"""
        traffic_light = TrafficLight(capacity=0.5, lost_time=0.0)
        return SignalGroup(id=name, traffic_lights=[traffic_light],
                           min_greenyellow=min_greenyellow, max_greenyellow=max_greenyellow, min_red=min_red,
                           max_red=max_red, min_nr=1, max_nr=3)

    @staticmethod
    def get_default_intersection(additional_signalgroups: Optional[List[SignalGroup]] = None
                                 ) -> Intersection:
        """
        Get a default intersection object with 2 conflicting signal groups "sg1" and "sg2"
        :param additional_signalgroups: signal groups to add to the intersection (besides signal group 'sg1' and 'sg2')
         (besides the conflict between signal group 'sg1' and 'sg2')
        :return: the intersection object
        """
        if additional_signalgroups is None:
            additional_signalgroups = []

        signalgroup1 = TestValidatingCompleteness.get_default_signalgroup(name="sg1")
        signalgroup2 = TestValidatingCompleteness.get_default_signalgroup(name="sg2")

        conflict = Conflict(id1="sg1", id2="sg2", setup12=2, setup21=3)

        intersection = Intersection(signalgroups=[signalgroup1, signalgroup2] + additional_signalgroups,
                                    conflicts=[conflict])

        return intersection

    def test_complete(self) -> None:
        # WHEN
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg2=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=60)]),
            period=100)
        intersection = TestValidatingCompleteness.get_default_intersection()

        # WHEN
        validate_completeness(intersection=intersection, fts=fts)

        # THEN no error should be raised

    def test_signalgroup_missing(self) -> None:
        # WHEN
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg2=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=60)]),
            period=100)
        signalgroup3 = TestValidatingCompleteness.get_default_signalgroup(name="sg3")
        intersection = TestValidatingCompleteness.get_default_intersection(additional_signalgroups=[signalgroup3])

        with self.assertRaises(SafetyViolation):
            # WHEN
            validate_completeness(intersection=intersection, fts=fts)

            # THEN no error should be raised

    def test_no_greenyellow_intervals(self) -> None:
        # WHEN
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg2=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=60)],
            sg3=[]),
            period=100)
        signalgroup3 = TestValidatingCompleteness.get_default_signalgroup(name="sg3")
        intersection = TestValidatingCompleteness.get_default_intersection(additional_signalgroups=[signalgroup3])

        with self.assertRaises(SafetyViolation):
            # WHEN
            validate_completeness(intersection=intersection, fts=fts)

            # THEN no error should be raised
