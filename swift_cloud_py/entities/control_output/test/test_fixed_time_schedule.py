import unittest
from typing import Dict

from swift_cloud_py.entities.control_output.fixed_time_schedule import GreenYellowInterval, FixedTimeSchedule
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight


class TestIntervalInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ Function to get default (valid) inputs for GreenYellowInterval() """
        return dict(start_greenyellow=82, end_greenyellow=1)

    def test_successful_validation(self) -> None:
        """ Test initializing GreenYellowInterval object with correct input """
        # GIVEN
        input_dict = TestIntervalInputValidation.get_default_inputs()

        # WHEN
        GreenYellowInterval(**input_dict)

        # THEN no error should be raised

    def test_not_a_number(self) -> None:
        """ Test initializing GreenYellowInterval object with non-numeric arguments """
        for key in TestIntervalInputValidation.get_default_inputs():
            # GIVEN
            input_dict = TestIntervalInputValidation.get_default_inputs()
            input_dict[key] = "str"  # each argument should be a number

            with self.assertRaises(ValueError):
                # WHEN initializing the queue lengths
                GreenYellowInterval(**input_dict)

                # THEN an error should be raised

    def test_negative(self) -> None:
        """ Test initializing GreenYellowInterval object with negative start_greenyellow or end_greenyellow"""
        for key in TestIntervalInputValidation.get_default_inputs():
            # GIVEN
            input_dict = TestIntervalInputValidation.get_default_inputs()
            input_dict[key] = -1  # should be positive

            with self.assertRaises(AssertionError):
                # WHEN initializing the queue lengths
                GreenYellowInterval(**input_dict)

                # THEN an error should be raised

    def test_comparing_success(self):
        """ Test comparing two of the same greenyellow intervals"""
        # GIVEN
        greenyellow1 = GreenYellowInterval(start_greenyellow=10, end_greenyellow=35)
        greenyellow2 = GreenYellowInterval(start_greenyellow=10, end_greenyellow=35)

        # WHEN
        same = greenyellow1 == greenyellow2

        # THEN
        self.assertTrue(same)

    def test_comparing_failure(self):
        """ Test comparing two different greenyellow intervals"""
        # GIVEN
        greenyellow1 = GreenYellowInterval(start_greenyellow=10, end_greenyellow=35)
        greenyellow2 = GreenYellowInterval(start_greenyellow=11, end_greenyellow=35)

        # WHEN
        same = greenyellow1 == greenyellow2

        # THEN
        self.assertEqual(same, False)


class TestIntervalJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestIntervalInputValidation.get_default_inputs()

        # WHEN
        greenyellow_interval = GreenYellowInterval(**input_dict)

        # THEN converting back and forth should in the end give the same result
        greenyellow_interval_list = greenyellow_interval.to_json()
        greenyellow_interval_from_json = GreenYellowInterval.from_json(
            greenyellow_interval_list=greenyellow_interval_list)
        self.assertListEqual(greenyellow_interval_list, greenyellow_interval_from_json.to_json())


class TestFTSInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ Function to get default (valid) inputs for GreenYellowInterval() """
        return dict(greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=82, end_greenyellow=1),
                                                    GreenYellowInterval(start_greenyellow=10, end_greenyellow=30)],
                                               sg2=[GreenYellowInterval(start_greenyellow=3, end_greenyellow=20)]),
                    period=100)

    def test_successful_validation(self) -> None:
        """ Test initializing GreenYellowInterval object with correct input """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()

        # WHEN
        FixedTimeSchedule(**input_dict)

        # THEN no error should be raised

    def test_no_dict(self) -> None:
        """ Test providing no dictionary for greenyellow_intervals"""
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        input_dict["greenyellow_intervals"] = 1

        with self.assertRaises(ValueError):
            # WHEN initializing the fts
            FixedTimeSchedule(**input_dict)

            # THEN an error should be raised

    def test_no_string_values(self) -> None:
        """ Test providing no string for each id in greenyellow_intervals"""
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        input_dict["greenyellow_intervals"][1] = [1, 2]  # add value (1) which is not a string

        with self.assertRaises(ValueError):
            # WHEN initializing the fts
            FixedTimeSchedule(**input_dict)

            # THEN an error should be raised

    def test_no_list_for_intervals(self) -> None:
        """ Test providing no list for the values in greenyellow_intervals"""
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        input_dict["greenyellow_intervals"]["id3"] = 1  # rates is not a list

        with self.assertRaises(ValueError):
            # WHEN initializing the fts
            FixedTimeSchedule(**input_dict)

            # THEN an error should be raised

    def test_rate_no_greenyellow_interval(self) -> None:
        """ Test providing no GreenYellowInterval for the interval """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        input_dict["greenyellow_intervals"]["id3"] = [GreenYellowInterval(start_greenyellow=1, end_greenyellow=10),
                                                      "3"]

        with self.assertRaises(ValueError):
            # WHEN initializing the fts
            FixedTimeSchedule(**input_dict)

            # THEN an error should be raised

    def test_times_exceeding_period_duration(self) -> None:
        """ Test providing no GreenYellowInterval for the interval """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for time in ["start_greenyellow", "end_greenyellow"]:
            with self.subTest(f"{time} exceeding period duration"):
                greenyellow_interval_dict = dict(start_greenyellow=1, end_greenyellow=10)
                greenyellow_interval_dict[time] = input_dict["period"] + 1
                input_dict["greenyellow_intervals"]["id3"] = [GreenYellowInterval(**greenyellow_interval_dict)]
                with self.assertRaises(ValueError):
                    # WHEN initializing the fts
                    FixedTimeSchedule(**input_dict)

                    # THEN an error should be raised

    def test_correct_order(self) -> None:
        """ Test providing GreenYellowInterval in the correct periodic order """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for first_interval in range(3):
            with self.subTest(f"first interval={first_interval}"):
                input_dict["greenyellow_intervals"]["id3"] = \
                    [GreenYellowInterval(start_greenyellow=0, end_greenyellow=20),
                     GreenYellowInterval(start_greenyellow=30, end_greenyellow=40),
                     GreenYellowInterval(start_greenyellow=50, end_greenyellow=60)]
                input_dict["greenyellow_intervals"]["id3"] = \
                    input_dict["greenyellow_intervals"]["id3"][first_interval:] + \
                    input_dict["greenyellow_intervals"]["id3"][:first_interval]

                # WHEN initializing the fts
                FixedTimeSchedule(**input_dict)

                # THEN no error should be raised

    def test_correct_order2(self) -> None:
        """ Test providing GreenYellowInterval in the correct periodic order """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for first_interval in range(3):
            with self.subTest(f"first interval={first_interval}"):
                input_dict["greenyellow_intervals"]["id3"] = \
                    [GreenYellowInterval(start_greenyellow=70, end_greenyellow=20),
                     GreenYellowInterval(start_greenyellow=30, end_greenyellow=40),
                     GreenYellowInterval(start_greenyellow=50, end_greenyellow=60)]
                input_dict["greenyellow_intervals"]["id3"] = \
                    input_dict["greenyellow_intervals"]["id3"][first_interval:] + \
                    input_dict["greenyellow_intervals"]["id3"][:first_interval]

                # WHEN initializing the fts
                FixedTimeSchedule(**input_dict)

                # THEN no error should be raised

    def test_wrong_order(self) -> None:
        """ Test providing GreenYellowInterval in the wrong periodic order """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for first_interval in range(3):
            with self.subTest(f"first interval={first_interval}"):
                input_dict["greenyellow_intervals"]["id3"] = \
                    [GreenYellowInterval(start_greenyellow=0, end_greenyellow=20),
                     GreenYellowInterval(start_greenyellow=50, end_greenyellow=60),
                     GreenYellowInterval(start_greenyellow=30, end_greenyellow=40)]
                input_dict["greenyellow_intervals"]["id3"] = \
                    input_dict["greenyellow_intervals"]["id3"][first_interval:] + \
                    input_dict["greenyellow_intervals"]["id3"][:first_interval]

                with self.assertRaises(ValueError):
                    # WHEN initializing the fts
                    FixedTimeSchedule(**input_dict)

                    # THEN an error should be raised

    def test_wrong_order2(self) -> None:
        """ Test providing GreenYellowInterval in the wrong periodic order """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for first_interval in range(3):
            with self.subTest(f"first interval={first_interval}"):
                input_dict["greenyellow_intervals"]["id3"] = \
                    [GreenYellowInterval(start_greenyellow=70, end_greenyellow=20),
                     GreenYellowInterval(start_greenyellow=50, end_greenyellow=60),
                     GreenYellowInterval(start_greenyellow=30, end_greenyellow=40)]
                input_dict["greenyellow_intervals"]["id3"] = \
                    input_dict["greenyellow_intervals"]["id3"][first_interval:] + \
                    input_dict["greenyellow_intervals"]["id3"][:first_interval]

                with self.assertRaises(ValueError):
                    # WHEN initializing the fts
                    FixedTimeSchedule(**input_dict)

                    # THEN an error should be raised

    def test_not_overlapping(self) -> None:
        """ Test providing non-overlapping GreenYellowInterval """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for first_interval in range(2):
            with self.subTest(f"first interval={first_interval}"):
                input_dict["greenyellow_intervals"]["id3"] = \
                    [GreenYellowInterval(start_greenyellow=0, end_greenyellow=20),
                     GreenYellowInterval(start_greenyellow=20, end_greenyellow=40)]  # at the verge of overlap
                input_dict["greenyellow_intervals"]["id3"] = \
                    input_dict["greenyellow_intervals"]["id3"][first_interval:] + \
                    input_dict["greenyellow_intervals"]["id3"][:first_interval]

                # WHEN initializing the fts
                FixedTimeSchedule(**input_dict)

                # THEN no error should be raised

    def test_not_overlapping2(self) -> None:
        """ Test providing non-overlapping GreenYellowInterval """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for first_interval in range(2):
            with self.subTest(f"first interval={first_interval}"):
                input_dict["greenyellow_intervals"]["id3"] = \
                    [GreenYellowInterval(start_greenyellow=70, end_greenyellow=20),
                     GreenYellowInterval(start_greenyellow=20, end_greenyellow=40)]  # at the verge of overlap
                input_dict["greenyellow_intervals"]["id3"] = \
                    input_dict["greenyellow_intervals"]["id3"][first_interval:] + \
                    input_dict["greenyellow_intervals"]["id3"][:first_interval]

                # WHEN initializing the fts
                FixedTimeSchedule(**input_dict)

                # THEN no error should be raised

    def test_overlapping(self) -> None:
        """ Test providing overlapping GreenYellowInterval """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for first_interval in range(2):
            with self.subTest(f"first interval={first_interval}"):
                input_dict["greenyellow_intervals"]["id3"] = \
                    [GreenYellowInterval(start_greenyellow=0, end_greenyellow=20),
                     GreenYellowInterval(start_greenyellow=15, end_greenyellow=40)]
                input_dict["greenyellow_intervals"]["id3"] = \
                    input_dict["greenyellow_intervals"]["id3"][first_interval:] + \
                    input_dict["greenyellow_intervals"]["id3"][:first_interval]

                with self.assertRaises(ValueError):
                    # WHEN initializing the fts
                    FixedTimeSchedule(**input_dict)

                    # THEN an error should be raised

    def test_overlapping2(self) -> None:
        """ Test providing overlapping GreenYellowInterval """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        for first_interval in range(2):
            with self.subTest(f"first interval={first_interval}"):
                input_dict["greenyellow_intervals"]["id3"] = \
                    [GreenYellowInterval(start_greenyellow=70, end_greenyellow=20),
                     GreenYellowInterval(start_greenyellow=15, end_greenyellow=40)]
                input_dict["greenyellow_intervals"]["id3"] = \
                    input_dict["greenyellow_intervals"]["id3"][first_interval:] + \
                    input_dict["greenyellow_intervals"]["id3"][:first_interval]

                with self.assertRaises(ValueError):
                    # WHEN initializing the fts
                    FixedTimeSchedule(**input_dict)

                    # THEN an error should be raised

    def test_comparing_success(self):
        """ Test comparing two equal fixed-time schedules """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        input_dict2 = TestFTSInputValidation.get_default_inputs()  # ensure not same references
        fts1 = FixedTimeSchedule(**input_dict)
        fts2 = FixedTimeSchedule(**input_dict2)

        # WHEN
        same = fts1 == fts2

        self.assertTrue(same)

    def test_comparing_different_period(self):
        """ Test comparing two different fixed-time schedules (different period) """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        input_dict2 = TestFTSInputValidation.get_default_inputs()  # ensure not same references
        input_dict2["period"] = input_dict["period"] * 2
        fts1 = FixedTimeSchedule(**input_dict)
        fts2 = FixedTimeSchedule(**input_dict2)

        # WHEN
        same = fts1 == fts2

        self.assertEqual(same, False)

    def test_comparing_different_ids(self):
        """ Test comparing two different fixed-time schedules (different ids) """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        input_dict2 = TestFTSInputValidation.get_default_inputs()  # ensure not same references
        input_dict2["greenyellow_intervals"]["sg3"] = input_dict2["greenyellow_intervals"]["sg2"]
        del input_dict2["greenyellow_intervals"]["sg2"]
        fts1 = FixedTimeSchedule(**input_dict)
        fts2 = FixedTimeSchedule(**input_dict2)

        # WHEN
        same = fts1 == fts2

        self.assertEqual(same, False)

    def test_comparing_different_greenyellow_intervals(self):
        """ Test comparing two different fixed-time schedules (different ids) """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()
        input_dict2 = TestFTSInputValidation.get_default_inputs()  # ensure not same references
        input_dict2["greenyellow_intervals"]["sg2"][0] = GreenYellowInterval(start_greenyellow=13, end_greenyellow=23)
        fts1 = FixedTimeSchedule(**input_dict)
        fts2 = FixedTimeSchedule(**input_dict2)

        # WHEN
        same = fts1 == fts2

        self.assertEqual(same, False)


class TestFTSMethods(unittest.TestCase):
    @staticmethod
    def get_default_fts_inputs() -> Dict:
        """ Function to get default (valid) inputs for GreenYellowInterval() """
        return dict(greenyellow_intervals=dict(sg1=[GreenYellowInterval(start_greenyellow=82, end_greenyellow=1),
                                                    GreenYellowInterval(start_greenyellow=10, end_greenyellow=30)],
                                               sg2=[GreenYellowInterval(start_greenyellow=3, end_greenyellow=20)]),
                    period=100)

    def test_retrieving_greenyellow_intervals(self):
        """ test retrieving all greenyellow intervals of a signal group """
        # GIVEN
        input_dict = TestFTSMethods.get_default_fts_inputs()
        sg1 = SignalGroup(id="sg1", traffic_lights=[TrafficLight(capacity=800, lost_time=1)],
                          min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)
        sg2 = SignalGroup(id="sg2", traffic_lights=[TrafficLight(capacity=800, lost_time=1)],
                          min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)

        # WHEN
        fts = FixedTimeSchedule(**input_dict)

        # THEN
        self.assertEqual(fts.get_greenyellow_intervals(signalgroup=sg1), input_dict["greenyellow_intervals"]["sg1"])
        self.assertEqual(fts.get_greenyellow_intervals(signalgroup=sg2), input_dict["greenyellow_intervals"]["sg2"])
        # using id should give the same result
        self.assertEqual(fts.get_greenyellow_intervals(signalgroup=sg1.id), input_dict["greenyellow_intervals"]["sg1"])
        self.assertEqual(fts.get_greenyellow_intervals(signalgroup=sg2.id), input_dict["greenyellow_intervals"]["sg2"])

    def test_retrieving_for_unkown_signalgroup(self):
        """ test retrieving greenyellow intervals of an unkown signal group """
        # GIVEN
        input_dict = TestFTSMethods.get_default_fts_inputs()
        # unkown signal group
        sg3 = SignalGroup(id="sg3", traffic_lights=[TrafficLight(capacity=800, lost_time=1)],
                          min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)

        fts = FixedTimeSchedule(**input_dict)

        with self.assertRaises(ValueError):
            # WHEN trying to access greenyellow intervals of an unkown signal group
            fts.get_greenyellow_intervals(sg3)

            # THEN an error should be raised

        # same but using id
        with self.assertRaises(ValueError):
            # WHEN trying to access greenyellow intervals of an unkown signal group
            fts.get_greenyellow_intervals(sg3.id)

            # THEN an error should be raised

    def test_retrieving_single_greenyellow_interval(self):
        """ test retrieving a single greenyellow interval of a signal group """
        # GIVEN
        input_dict = TestFTSMethods.get_default_fts_inputs()
        sg1 = SignalGroup(id="sg1", traffic_lights=[TrafficLight(capacity=800, lost_time=1)],
                          min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)
        sg2 = SignalGroup(id="sg2", traffic_lights=[TrafficLight(capacity=800, lost_time=1)],
                          min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)

        # WHEN
        fts = FixedTimeSchedule(**input_dict)

        # THEN
        self.assertEqual(fts.get_greenyellow_interval(signalgroup=sg1, k=0),
                         input_dict["greenyellow_intervals"]["sg1"][0])
        self.assertEqual(fts.get_greenyellow_interval(signalgroup=sg1, k=1),
                         input_dict["greenyellow_intervals"]["sg1"][1])

        self.assertEqual(fts.get_greenyellow_interval(signalgroup=sg2, k=0),
                         input_dict["greenyellow_intervals"]["sg2"][0])

    def test_retrieving_single_interval_for_unkown_signalgroup(self):
        """ test retrieving greenyellow intervals of an unkown signal group """
        # GIVEN
        input_dict = TestFTSMethods.get_default_fts_inputs()
        # unkown signal group
        sg3 = SignalGroup(id="sg3", traffic_lights=[TrafficLight(capacity=800, lost_time=1)],
                          min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)

        fts = FixedTimeSchedule(**input_dict)

        with self.assertRaises(ValueError):
            # WHEN trying to access greenyellow intervals of an unkown signal group
            fts.get_greenyellow_interval(sg3, k=0)

            # THEN an error should be raised

    def test_retrieving_unkown_interval(self):
        """ test retrieving greenyellow intervals of an unkown signal group """
        # GIVEN
        input_dict = TestFTSMethods.get_default_fts_inputs()
        # unkown signal group
        sg1 = SignalGroup(id="sg1", traffic_lights=[TrafficLight(capacity=800, lost_time=1)],
                          min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)

        fts = FixedTimeSchedule(**input_dict)

        with self.assertRaises(ValueError):
            # WHEN trying to access greenyellow intervals of an unkown signal group
            fts.get_greenyellow_interval(sg1, k=2)  # has only 2 intervals (with indices k=0 and k=1)

            # THEN an error should be raised


class TestFTSJsonConversion(unittest.TestCase):

    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestFTSInputValidation.get_default_inputs()

        # WHEN
        fixed_time_schedule = FixedTimeSchedule(**input_dict)

        # THEN converting back and forth should in the end give the same result
        fts_dict = fixed_time_schedule.to_json()
        fts_from_json = FixedTimeSchedule.from_json(fts_dict=fts_dict)
        self.assertDictEqual(fts_dict, fts_from_json.to_json())
