import unittest
from typing import Dict

from swift_cloud_py.entities.control_output.fixed_time_schedule import GreenYellowInterval


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


class TestJsonConversion(unittest.TestCase):
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
