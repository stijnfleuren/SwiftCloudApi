import unittest
from copy import deepcopy
from typing import Optional, List

from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule, GreenYellowInterval
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.sg_relations import Conflict
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates
from swift_cloud_py.validate_safety_restrictions.validate_bounds import validate_bounds


class TestFTSValidationOfBounds(unittest.TestCase):
    """ Test whether a minimum or a maximum greenyellow time (or red time) is violated """

    @staticmethod
    def get_default_signalgroup(name: str, min_greenyellow: float = 10.0, max_greenyellow: float = 80.0,
                                min_red: float = 10.0, max_red: float = 80.0) -> SignalGroup:
        """ Get a default signalgroup object"""
        traffic_light = TrafficLight(capacity=0.5, lost_time=0.0)
        return SignalGroup(id=name, traffic_lights=[traffic_light],
                           min_greenyellow=min_greenyellow, max_greenyellow=max_greenyellow, min_red=min_red,
                           max_red=max_red, min_nr=1, max_nr=3)

    @staticmethod
    def get_default_intersection(additional_signalgroups: Optional[List[SignalGroup]] = None,
                                 additional_conflicts: Optional[List[Conflict]] = None,
                                 ) -> Intersection:
        """
        Get a default intersection object with 2 conflicting signal groups "sg1" and "sg2"
        :param additional_signalgroups: signal groups to add to the intersection (besides signal group 'sg1' and 'sg2')
        :param additional_conflicts: additional conflicts to add
         (besides the conflict between signal group 'sg1' and 'sg2')
        :return: the intersection object
        """
        if additional_signalgroups is None:
            additional_signalgroups = []
        if additional_conflicts is None:
            additional_conflicts = []

        signalgroup1 = TestFTSValidationOfBounds.get_default_signalgroup(name="sg1")
        signalgroup2 = TestFTSValidationOfBounds.get_default_signalgroup(name="sg2")

        conflict = Conflict(id1="sg1", id2="sg2", setup12=2, setup21=3)

        intersection = Intersection(signalgroups=[signalgroup1, signalgroup2] + additional_signalgroups,
                                    conflicts=[conflict] + additional_conflicts)

        return intersection

    @staticmethod
    def get_arrival_rates(signalgroups: List[SignalGroup]):
        id_to_arrival_rates = {signalgroup.id: 100 for signalgroup in signalgroups}
        return ArrivalRates(id_to_arrival_rates=id_to_arrival_rates)

    def test_successful_validation(self) -> None:
        """ Test validating correct fts; we will modify this schedule to violate minimum green and red times """
        # GIVEN
        fts = FixedTimeSchedule(
            greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=0, end_greenyellow=10),
                                            GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
                                       sg2=[GreenYellowInterval(start_greenyellow=30, end_greenyellow=45),
                                            GreenYellowInterval(start_greenyellow=75, end_greenyellow=95)]), period=100)
        intersection = TestFTSValidationOfBounds.get_default_intersection()

        # WHEN
        validate_bounds(intersection=intersection, fts=fts)

        # THEN no error should be raised

    def test_green_interval_too_small(self) -> None:
        """ Test green interval too short """
        # GIVEN
        fts_org = FixedTimeSchedule(
            greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=0, end_greenyellow=10),
                                            GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
                                       sg2=[GreenYellowInterval(start_greenyellow=30, end_greenyellow=45),
                                            GreenYellowInterval(start_greenyellow=75, end_greenyellow=95)]), period=100)

        intersection = TestFTSValidationOfBounds.get_default_intersection()

        for signal_group_id, index in [("sg1", 0), ("sg1", 1), ("sg2", 0), ("sg2", 1)]:
            with self.subTest(f"green interval {index} to small for sg={signal_group_id}"):
                with self.assertRaises(SafetyViolation):
                    fts = deepcopy(fts_org)

                    # change the greenyellow interval to have a duration of only 5 seconds
                    fts._greenyellow_intervals[signal_group_id][index].end_greenyellow = \
                        (fts._greenyellow_intervals[signal_group_id][index].start_greenyellow + 5) % fts.period
                    # WHEN validating
                    validate_bounds(intersection=intersection, fts=fts)

                    # THEN an error should be raised

    def test_red_interval_too_small(self) -> None:
        """ Test red interval too short """
        # GIVEN
        fts_org = FixedTimeSchedule(
            greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=0, end_greenyellow=10),
                                            GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
                                       sg2=[GreenYellowInterval(start_greenyellow=30, end_greenyellow=45),
                                            GreenYellowInterval(start_greenyellow=75, end_greenyellow=95)]), period=100)

        intersection = TestFTSValidationOfBounds.get_default_intersection()

        for signal_group_id, index in [("sg1", 0), ("sg1", 1), ("sg2", 0), ("sg2", 1)]:
            with self.subTest(f"red interval {index} to small for sg={signal_group_id}"):
                with self.assertRaises(SafetyViolation):
                    fts = deepcopy(fts_org)
                    prev_index = (index - 1) % 2

                    # red time of only 5 seconds
                    fts._greenyellow_intervals[signal_group_id][index].start_greenyellow = \
                        (fts._greenyellow_intervals[signal_group_id][prev_index].end_greenyellow + 5) % 100
                    # WHEN validating
                    validate_bounds(intersection=intersection, fts=fts)

                    # THEN an error should be raised

    def test_successful_validation2(self) -> None:
        """ Test validation for correct fts; we will modify this schedule to violate maximum green and red times """
        # GIVEN
        fts = FixedTimeSchedule(
            greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=0, end_greenyellow=50),
                                            GreenYellowInterval(start_greenyellow=120, end_greenyellow=170)],
                                       sg2=[GreenYellowInterval(start_greenyellow=60, end_greenyellow=110),
                                            GreenYellowInterval(start_greenyellow=180, end_greenyellow=230)]),
            period=240)

        intersection = TestFTSValidationOfBounds.get_default_intersection()

        # WHEN
        validate_bounds(intersection=intersection, fts=fts)

        # THEN no error should be raised

    def test_green_interval_too_large(self) -> None:
        """ Test green interval too large """
        # GIVEN
        # green interval of signalgroup 3 is too large
        fts = FixedTimeSchedule(
            greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=0, end_greenyellow=50),
                                            GreenYellowInterval(start_greenyellow=120, end_greenyellow=170)],
                                       sg2=[GreenYellowInterval(start_greenyellow=60, end_greenyellow=110),
                                            GreenYellowInterval(start_greenyellow=180, end_greenyellow=230)],
                                       sg3=[GreenYellowInterval(start_greenyellow=0, end_greenyellow=80),
                                            GreenYellowInterval(start_greenyellow=120, end_greenyellow=170)]),
            period=240)

        signalgroup3 = TestFTSValidationOfBounds.get_default_signalgroup(name="sg3", max_greenyellow=40)
        intersection = TestFTSValidationOfBounds.get_default_intersection(additional_signalgroups=[signalgroup3])

        with self.assertRaises(SafetyViolation):
            # WHEN validating
            validate_bounds(intersection=intersection, fts=fts)

            # THEN an error should be raised

    def test_red_interval_too_large(self) -> None:
        """ Test red interval too large """
        # GIVEN
        # red interval of signalgroup 3 is too large
        fts = FixedTimeSchedule(
            greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=0, end_greenyellow=50),
                                            GreenYellowInterval(start_greenyellow=120, end_greenyellow=170)],
                                       sg2=[GreenYellowInterval(start_greenyellow=60, end_greenyellow=110),
                                            GreenYellowInterval(start_greenyellow=180, end_greenyellow=230)],
                                       sg3=[GreenYellowInterval(start_greenyellow=0, end_greenyellow=50),
                                            GreenYellowInterval(start_greenyellow=120, end_greenyellow=170)]),
            period=240)

        signalgroup3 = TestFTSValidationOfBounds.get_default_signalgroup(name="sg3", max_red=60)
        intersection = TestFTSValidationOfBounds.get_default_intersection(additional_signalgroups=[signalgroup3])

        with self.assertRaises(SafetyViolation):
            # WHEN validating
            validate_bounds(intersection=intersection, fts=fts)

            # THEN an error should be raised
