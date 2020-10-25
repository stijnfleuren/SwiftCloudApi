import unittest
from copy import deepcopy
from itertools import product

from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule, GreenYellowInterval
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.sg_relations import Conflict
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight
from swift_cloud_py.validate_safety_restrictions.validate_conflicts import validate_conflicts


class TestFTSConflictValidation(unittest.TestCase):
    """ unittests for validating satisfying conflicts and the associated minimum clearance times """

    @staticmethod
    def get_default_signalgroup(name: str, min_greenyellow: float = 10.0, max_greenyellow: float = 80.0,
                                min_red: float = 10.0, max_red: float = 80.0) -> SignalGroup:
        """ Get a default signalgroup object"""
        traffic_light = TrafficLight(capacity=0.5, lost_time=0.0)
        return SignalGroup(id=name, traffic_lights=[traffic_light],
                           min_greenyellow=min_greenyellow, max_greenyellow=max_greenyellow, min_red=min_red,
                           max_red=max_red, min_nr=1, max_nr=3)

    def test_conflict_satisfied(self) -> None:
        """
        test that validations pass if constraints are satisfied
        :return:
        """
        # GIVEN
        signalgroup1 = TestFTSConflictValidation.get_default_signalgroup(name="sg1")
        signalgroup2 = TestFTSConflictValidation.get_default_signalgroup(name="sg2")

        conflict = Conflict(id1="sg1", id2="sg2", setup12=2, setup21=3)

        intersection = Intersection(signalgroups=[signalgroup1, signalgroup2], conflicts=[conflict])

        fts = FixedTimeSchedule(
            greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=90, end_greenyellow=10),
                                            GreenYellowInterval(start_greenyellow=33, end_greenyellow=60)],
                                       sg2=[GreenYellowInterval(start_greenyellow=12, end_greenyellow=30),
                                            GreenYellowInterval(start_greenyellow=62, end_greenyellow=87)]), period=100)

        for interval_shift in range(2):
            with self.subTest(f"interval_shift={interval_shift}"):
                fts._greenyellow_intervals["sg2"] = \
                    fts._greenyellow_intervals["sg2"][:interval_shift] + \
                    fts._greenyellow_intervals["sg2"][interval_shift:]
                # WHEN validating
                validate_conflicts(intersection=intersection, fts=fts)

                # THEN no error should be raised

    def test_violating_conflict(self) -> None:
        """
        test that validations fails if minimum clearance times are violated.
        """
        # GIVEN
        signalgroup1 = TestFTSConflictValidation.get_default_signalgroup(name="sg1")
        signalgroup2 = TestFTSConflictValidation.get_default_signalgroup(name="sg2")

        conflict = Conflict(id1="sg1", id2="sg2", setup12=2, setup21=3)

        intersection = Intersection(signalgroups=[signalgroup1, signalgroup2], conflicts=[conflict])

        fts = FixedTimeSchedule(
            greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=90, end_greenyellow=10),
                                            GreenYellowInterval(start_greenyellow=33, end_greenyellow=60)],
                                       sg2=[GreenYellowInterval(start_greenyellow=12, end_greenyellow=30),
                                            GreenYellowInterval(start_greenyellow=62, end_greenyellow=87)]), period=100)

        for signalgroup_id, interval_index, interval_shift in product(["sg1", "sg2"], [0, 1], [0]):
            with self.subTest(f"signalgroup_id={signalgroup_id}, interval_index={interval_index}, "
                              f"interval_shift={interval_shift}"):
                # adjusting schedule such that the start of greenyellow interval 'interval_index' of signalgroup_id
                # violates the minimum clearance time
                fts_copy = deepcopy(fts)
                if signalgroup_id == "sg1":
                    fts_copy._greenyellow_intervals["sg1"][interval_index].start_greenyellow = \
                        (fts_copy._greenyellow_intervals["sg2"][(interval_index + 1) % 2].end_greenyellow +
                         conflict.setup21 - 1) % fts_copy.period
                if signalgroup_id == "sg2":
                    fts_copy._greenyellow_intervals["sg2"][interval_index].start_greenyellow = \
                        (fts_copy._greenyellow_intervals["sg1"][interval_index].end_greenyellow +
                         conflict.setup12 - 1) % fts_copy.period

                fts_copy._greenyellow_intervals["sg2"] = fts_copy._greenyellow_intervals["sg2"][:interval_shift] + \
                    fts_copy._greenyellow_intervals["sg2"][interval_shift:]

                with self.assertRaises(SafetyViolation):
                    # WHEN validating
                    validate_conflicts(intersection=intersection, fts=fts_copy)

                    # THEN an error should be raised
