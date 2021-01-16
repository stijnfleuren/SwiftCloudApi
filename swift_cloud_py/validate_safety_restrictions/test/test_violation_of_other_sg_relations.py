import unittest
from copy import deepcopy
from typing import List, Optional

from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule, GreenYellowInterval
from swift_cloud_py.entities.intersection.sg_relations import SyncStart, Offset, PreStart, Conflict
from swift_cloud_py.validate_safety_restrictions.validate_other_sg_relations import find_other_sg_relation_matches, \
    get_shift_of_one_to_one_match, get_other_sg_relation_shift, validate_other_sg_relations


class TestFindOtherRelationMatches(unittest.TestCase):
    """ Unittests of the function find_other_sg_relation_matches """

    def test_zero_shift(self) -> None:
        """ Test finding a shift of zero """
        # GIVEN
        sync_start = SyncStart(from_id="sg1", to_id="sg2")
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg2=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=60)]),
            period=100)

        # WHEN
        matches = find_other_sg_relation_matches(other_relation=sync_start, fts=fts, index_from=0)
        matches2 = find_other_sg_relation_matches(other_relation=sync_start, fts=fts, index_from=1)

        # THEN
        self.assertListEqual(matches, [1, 0])
        self.assertListEqual(matches2, [0, 1])

    def test_shift_one(self) -> None:
        """ Test finding a shift of one """
        # GIVEN
        sync_start = SyncStart(from_id="sg1", to_id="sg2")
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg2=[GreenYellowInterval(start_greenyellow=50, end_greenyellow=60),
                 GreenYellowInterval(start_greenyellow=10, end_greenyellow=30)]),
            period=100)

        # WHEN
        matches = find_other_sg_relation_matches(other_relation=sync_start, fts=fts, index_from=0)
        matches2 = find_other_sg_relation_matches(other_relation=sync_start, fts=fts, index_from=1)

        # THEN
        self.assertListEqual(matches, [0, 1])
        self.assertListEqual(matches2, [1, 0])

    def test_no_shift_possible(self) -> None:
        """ Test finding the shifts for a schedule without an unambiguous shift"""
        # GIVEN
        sync_start = SyncStart(from_id="sg1", to_id="sg2")
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=40, end_greenyellow=50),
                 GreenYellowInterval(start_greenyellow=60, end_greenyellow=80)],
            sg2=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=40, end_greenyellow=50),
                 GreenYellowInterval(start_greenyellow=60, end_greenyellow=80)]),
            period=100)

        # swap two intervals (we do this after initialization as otherwise we would get a ValueError (not correct order
        #  of greenyellow intervals) when initializing the FixedTimeSchedule
        fts._greenyellow_intervals["sg2"][:2] = reversed(fts._greenyellow_intervals["sg2"][:2])

        # WHEN
        matches = find_other_sg_relation_matches(other_relation=sync_start, fts=fts, index_from=0)
        matches2 = find_other_sg_relation_matches(other_relation=sync_start, fts=fts, index_from=1)
        matches3 = find_other_sg_relation_matches(other_relation=sync_start, fts=fts, index_from=2)

        # THEN
        self.assertListEqual(matches, [0, 1, 0])
        self.assertListEqual(matches2, [1, 0, 0])
        self.assertListEqual(matches3, [0, 0, 1])


class TestGetOneToOneMatch(unittest.TestCase):
    """ Unittests of the function get_shift_of_one_to_one_match """

    def test_zero_shift(self) -> None:
        """ Test finding a shift of zero """
        # GIVEN (matches has a diagonal of True values indicating a shift of zero)
        matches = [[True, False, True], [False, True, False], [True, False, True]]

        # WHEN
        shift = get_shift_of_one_to_one_match(matches=matches)

        # THEN
        self.assertEqual(shift, 0)

    def test_shift_of_one(self) -> None:
        """ Test finding a shift of one """
        # GIVEN
        matches = [[False, True, True], [False, True, True], [True, False, False]]

        # WHEN
        shift = get_shift_of_one_to_one_match(matches=matches)

        # THEN
        self.assertEqual(shift, 1)

    def test_no_shift_possible(self) -> None:
        """ Test finding no shift is possible if matches shows no unambiguous shift"""
        # GIVEN
        matches = [[False, False, True], [False, True, True], [True, False, False]]

        # WHEN
        shift = get_shift_of_one_to_one_match(matches=matches)

        # THEN
        self.assertEqual(shift, None)


class TestGetOtherRelationShift(unittest.TestCase):
    """ Unittests of the function get_other_sg_relation_shift """

    def test_zero_shift(self) -> None:
        """ Test finding a shift of zero """
        # GIVEN
        sync_start = SyncStart(from_id="sg1", to_id="sg2")
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg2=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=80)]),
            period=100)

        # WHEN
        shift = get_other_sg_relation_shift(other_relation=sync_start, fts=fts)

        # THEN
        self.assertEqual(shift, 0)

    def test_shift_of_one(self) -> None:
        """ Test finding a shift of one """
        # GIVEN
        sync_start = SyncStart(from_id="sg1", to_id="sg2")
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg2=[GreenYellowInterval(start_greenyellow=50, end_greenyellow=80),
                 GreenYellowInterval(start_greenyellow=10, end_greenyellow=30)]),
            period=100)

        # WHEN
        shift = get_other_sg_relation_shift(other_relation=sync_start, fts=fts)

        # THEN
        self.assertEqual(shift, 1)

    def test_no_shift_possible(self) -> None:
        """ Test finding no shift is possible for a schedule without an unambiguous shift"""
        # GIVEN
        sync_start = SyncStart(from_id="sg1", to_id="sg2")
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=40, end_greenyellow=50),
                 GreenYellowInterval(start_greenyellow=60, end_greenyellow=80)],
            sg2=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=40, end_greenyellow=50),
                 GreenYellowInterval(start_greenyellow=60, end_greenyellow=80)]),
            period=100)

        # Swap two intervals (we do this after initialization as otherwise we would get a ValueError (not correct order
        #  of greenyellow intervals)
        fts._greenyellow_intervals["sg2"][:2] = reversed(fts._greenyellow_intervals["sg2"][:2])

        # WHEN
        shift = get_other_sg_relation_shift(other_relation=sync_start, fts=fts)

        # THEN
        self.assertEqual(shift, None)


class TestFTSOtherSGRelationValidation(unittest.TestCase):
    """ Test validation of other  sg relations (synchronous starts, offsets, prestarts,...)"""

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
                                 sync_starts: List[SyncStart] = None,
                                 offsets: List[Offset] = None,
                                 prestarts: List[PreStart] = None,
                                 ) -> Intersection:
        """
        Get a default intersection object with 2 conflicting signal groups "sg1" and "sg2"
        :param additional_signalgroups: signal groups to add to the intersection (besides signal group 'sg1' and 'sg2')
        :param sync_starts: SyncStarts that must be satisfied
        :param offsets: Coordinations that must be satisfied
        :param prestarts: PreStarts that must be satisfied
        :return: the intersection object
        """
        if additional_signalgroups is None:
            additional_signalgroups = []

        if sync_starts is None:
            sync_starts = []
        if offsets is None:
            offsets = []
        if prestarts is None:
            prestarts = []

        signalgroup1 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg1")
        signalgroup2 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg2")

        conflict = Conflict(id1="sg1", id2="sg2", setup12=2, setup21=3)

        intersection = Intersection(signalgroups=[signalgroup1, signalgroup2] + additional_signalgroups,
                                    conflicts=[conflict], sync_starts=sync_starts, offsets=offsets,
                                    prestarts=prestarts)

        return intersection

    def test_correct_sync_starts(self) -> None:
        """
        Test that validation of correct synchronous start passes.
        :return:
        """
        # GIVEN
        sync_start = SyncStart(from_id="sg3", to_id="sg4")
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=15, end_greenyellow=35)],
            sg2=[GreenYellowInterval(start_greenyellow=45, end_greenyellow=65)],
            sg3=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg4=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=60)]),
            period=100)
        signalgroup3 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg3")
        signalgroup4 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg4")
        intersection = TestFTSOtherSGRelationValidation.get_default_intersection(
            additional_signalgroups=[signalgroup3, signalgroup4], sync_starts=[sync_start])

        # WHEN validating
        validate_other_sg_relations(intersection=intersection, fts=fts)

        # THEN no error should be raised

    def test_incorrect_sync_starts(self) -> None:
        """
        Test that validation of incorrect synchronous start raises SafetyViolation.
        :return:
        """
        # GIVEN
        sync_start = SyncStart(from_id="sg3", to_id="sg4")
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=15, end_greenyellow=35)],
            sg2=[GreenYellowInterval(start_greenyellow=45, end_greenyellow=65)],
            sg3=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg4=[GreenYellowInterval(start_greenyellow=9, end_greenyellow=30),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=60)]),
            period=100)
        signalgroup3 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg3")
        signalgroup4 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg4")
        intersection = TestFTSOtherSGRelationValidation.get_default_intersection(
            additional_signalgroups=[signalgroup3, signalgroup4], sync_starts=[sync_start])

        with self.assertRaises(SafetyViolation):
            # WHEN validating
            validate_other_sg_relations(intersection=intersection, fts=fts)

            # THEN an error should be raised

    def test_correct_offset(self) -> None:
        """
        Test that validation of correct offset passes.
        :return:
        """
        # GIVEN
        offset = Offset(from_id="sg3", to_id="sg4", seconds=20)
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=15, end_greenyellow=35)],
            sg2=[GreenYellowInterval(start_greenyellow=45, end_greenyellow=65)],
            sg3=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg4=[GreenYellowInterval(start_greenyellow=30, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=70, end_greenyellow=90)]),
            period=100)
        signalgroup3 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg3")
        signalgroup4 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg4")
        intersection = TestFTSOtherSGRelationValidation.get_default_intersection(
            additional_signalgroups=[signalgroup3, signalgroup4], offsets=[offset])

        for interval_shift in range(2):
            with self.subTest(f"interval_shift={interval_shift}"):
                fts_copy = deepcopy(fts)
                fts_copy._greenyellow_intervals["sg4"] = fts_copy._greenyellow_intervals["sg4"][:interval_shift] + \
                    fts_copy._greenyellow_intervals["sg4"][interval_shift:]
                # WHEN validating
                validate_other_sg_relations(intersection=intersection, fts=fts_copy)

                # THEN no error should be raised

    def test_incorrect_offset(self) -> None:
        """
        Test that validation of incorrect offset raises SafetyViolation.
        :return:
        """
        # GIVEN
        offset = Offset(from_id="sg3", to_id="sg4", seconds=20)
        fts_org = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=15, end_greenyellow=35)],
            sg2=[GreenYellowInterval(start_greenyellow=45, end_greenyellow=65)],
            sg3=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg4=[GreenYellowInterval(start_greenyellow=30, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=69, end_greenyellow=90)]),
            period=100)
        signalgroup3 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg3")
        signalgroup4 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg4")
        intersection = TestFTSOtherSGRelationValidation.get_default_intersection(
            additional_signalgroups=[signalgroup3, signalgroup4], offsets=[offset])

        for interval_shift in range(2):
            with self.subTest(f"interval_shift={interval_shift}"):
                fts = deepcopy(fts_org)
                fts._greenyellow_intervals["sg4"] = fts._greenyellow_intervals["sg4"][:interval_shift] + \
                    fts._greenyellow_intervals["sg4"][interval_shift:]

                with self.assertRaises(SafetyViolation):
                    # WHEN validating
                    validate_other_sg_relations(intersection=intersection, fts=fts)

                    # THEN a SafetyViolation error should be raised

    def test_correct_prestart(self) -> None:
        """
        Test that validation of correct prestart passes.
        :return:
        """
        # GIVEN
        min_prestart = 20
        max_prestart = 30
        prestart = PreStart(from_id="sg3", to_id="sg4", min_seconds=min_prestart, max_seconds=max_prestart)
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=15, end_greenyellow=35)],
            sg2=[GreenYellowInterval(start_greenyellow=45, end_greenyellow=65)],
            sg3=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg4=[GreenYellowInterval(start_greenyellow=30, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=69, end_greenyellow=90)]),
            period=100)
        signalgroup3 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg3")
        signalgroup4 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg4")
        intersection = TestFTSOtherSGRelationValidation.get_default_intersection(
            additional_signalgroups=[signalgroup3, signalgroup4], prestarts=[prestart])

        for pre_start_time in [min_prestart, max_prestart]:
            for interval_shift in range(2):
                fts_copy = deepcopy(fts)

                # adjust schedule to the specified prestart
                for index, greenyellow_interval in enumerate(fts_copy.get_greenyellow_intervals(signalgroup4)):
                    greenyellow_start = (greenyellow_interval.start_greenyellow - pre_start_time) % fts_copy.period
                    greenyellow_end = (greenyellow_start + 20) % fts_copy.period
                    fts_copy._greenyellow_intervals["sg3"][index] = GreenYellowInterval(
                        start_greenyellow=greenyellow_start, end_greenyellow=greenyellow_end)

                fts_copy._greenyellow_intervals["sg4"] = fts_copy._greenyellow_intervals["sg4"][:interval_shift] + \
                    fts_copy._greenyellow_intervals["sg4"][interval_shift:]

                with self.subTest(f"prestart={pre_start_time}, interval_shift={interval_shift}"):
                    # WHEN validating
                    validate_other_sg_relations(intersection=intersection, fts=fts_copy)

                    # THEN no error should be raised

    def test_incorrect_prestart(self) -> None:
        """
        Test that validation of incorrect prestart raises SafetyViolation.
        :return:
        """
        # GIVEN
        min_prestart = 20
        max_prestart = 30
        prestart = PreStart(from_id="sg3", to_id="sg4", min_seconds=min_prestart, max_seconds=max_prestart)
        fts = FixedTimeSchedule(greenyellow_intervals=dict(
            sg1=[GreenYellowInterval(start_greenyellow=15, end_greenyellow=35)],
            sg2=[GreenYellowInterval(start_greenyellow=45, end_greenyellow=65)],
            sg3=[GreenYellowInterval(start_greenyellow=10, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=50, end_greenyellow=70)],
            sg4=[GreenYellowInterval(start_greenyellow=30, end_greenyellow=40),
                 GreenYellowInterval(start_greenyellow=69, end_greenyellow=90)]),
            period=100)
        signalgroup3 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg3")
        signalgroup4 = TestFTSOtherSGRelationValidation.get_default_signalgroup(name="sg4")
        intersection = TestFTSOtherSGRelationValidation.get_default_intersection(
            additional_signalgroups=[signalgroup3, signalgroup4], prestarts=[prestart])

        for pre_start_time in [min_prestart - 1, max_prestart + 1]:
            for interval_shift in range(2):
                fts_copy = deepcopy(fts)

                # adjust schedule to the specified prestart
                for index, greenyellow_interval in enumerate(fts_copy.get_greenyellow_intervals(signalgroup4)):
                    greenyellow_start = (greenyellow_interval.start_greenyellow - pre_start_time) % fts_copy.period
                    greenyellow_end = (greenyellow_start + 20) % fts_copy.period
                    fts_copy._greenyellow_intervals["sg3"][index] = GreenYellowInterval(
                        start_greenyellow=greenyellow_start, end_greenyellow=greenyellow_end)

                fts_copy._greenyellow_intervals["sg4"] = fts_copy._greenyellow_intervals["sg4"][:interval_shift] + \
                    fts_copy._greenyellow_intervals["sg4"][interval_shift:]

                with self.subTest(f"prestart={pre_start_time}, interval_shift={interval_shift}"):
                    with self.assertRaises(SafetyViolation):
                        # WHEN validating
                        validate_other_sg_relations(intersection=intersection, fts=fts_copy)

                        # THEN a SafetyViolation should be raised
