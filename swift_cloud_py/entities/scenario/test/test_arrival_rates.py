import unittest
from typing import Dict

from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


class TestInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ Function to get default (valid) inputs for ArrivalRates() """
        return dict(id_to_arrival_rates={"1": [1000, 950], "2": [850, 700]})

    def test_successful_validation(self) -> None:
        """ Test initializing ArrivalRates object with correct input """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        ArrivalRates(**input_dict)

        # THEN no error should be raised

    def test_no_dict(self) -> None:
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id_to_arrival_rates"] = 1

        with self.assertRaises(ValueError):
            # WHEN initializing the arrival rates
            ArrivalRates(**input_dict)

            # THEN an error should be raised

    def test_no_string_values(self) -> None:
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id_to_arrival_rates"][1] = [1, 2]  # add value (1) which is not a string

        with self.assertRaises(ValueError):
            # WHEN initializing the arrival rates
            ArrivalRates(**input_dict)

            # THEN an error should be raised

    def test_no_list_for_rates(self) -> None:
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id_to_arrival_rates"]["3"] = 1  # rates is not a list

        with self.assertRaises(ValueError):
            # WHEN initializing the arrival rates
            ArrivalRates(**input_dict)

            # THEN an error should be raised

    def test_rate_no_number(self) -> None:
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id_to_arrival_rates"]["3"] = [1, "3"]  # rates is not a list of numbers

        with self.assertRaises(ValueError):
            # WHEN initializing the arrival rates
            ArrivalRates(**input_dict)

            # THEN an error should be raised


class TestOperations(unittest.TestCase):

    def test_multiply(self) -> None:
        """ Test multiplying ArrivalRates """
        # GIVEN
        arrival_rates1 = ArrivalRates(id_to_arrival_rates={"1": [1000, 950], "2": [850, 700]})

        # WHEN
        arrival_rates1 *= 1.3

        # THEN
        self.assertListEqual(arrival_rates1.id_to_arrival_rates["1"], [1000 * 1.3, 950 * 1.3])
        self.assertListEqual(arrival_rates1.id_to_arrival_rates["2"], [850 * 1.3, 700 * 1.3])

    def test_multiply_wrong_type(self) -> None:
        """ Test multiplying ArrivalRates with non-numeric value """
        # GIVEN
        arrival_rates1 = ArrivalRates(id_to_arrival_rates={"1": [1000, 950], "2": [850, 700]})

        with self.assertRaises(ArithmeticError):
            # WHEN
            arrival_rates1 *= "string"

            # THEN an exception should be raised

    def test_add(self) -> None:
        """ Test adding two ArrivalRates """
        # GIVEN
        arrival_rates1 = ArrivalRates(id_to_arrival_rates={"1": [1000, 950], "2": [850, 700]})
        arrival_rates2 = ArrivalRates(id_to_arrival_rates={"1": [642, 230], "2": [600, 355]})

        # WHEN
        arrival_rates1 += arrival_rates2

        # THEN
        self.assertListEqual(arrival_rates1.id_to_arrival_rates["1"], [1000 + 642, 950 + 230])
        self.assertListEqual(arrival_rates1.id_to_arrival_rates["2"], [850 + 600, 700 + 355])

    def test_add_different_ids(self) -> None:
        """ Test adding two ArrivalRates with different ids """
        # GIVEN
        arrival_rates1 = ArrivalRates(id_to_arrival_rates={"1": [1000, 950], "2": [850, 700]})
        arrival_rates2 = ArrivalRates(id_to_arrival_rates={"1": [642, 230], "3": [600, 355]})

        with self.assertRaises(ArithmeticError):
            # WHEN adding to rates with different ids
            arrival_rates1 + arrival_rates2

            # THEN an assertion should be raised

    def test_add_different_lengths(self) -> None:
        """ Test adding two ArrivalRates with different number of rates """
        # GIVEN
        arrival_rates1 = ArrivalRates(id_to_arrival_rates={"1": [1000, 950], "2": [850, 700]})
        arrival_rates2 = ArrivalRates(id_to_arrival_rates={"1": [642, 230], "2": [600, 355, 800]})

        with self.assertRaises(ArithmeticError):
            # WHEN adding to rates with different ids
            arrival_rates1 + arrival_rates2

            # THEN an assertion should be raised


class TestJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        arrival_rates = ArrivalRates(**input_dict)

        # THEN converting back and forth should in the end give the same result
        arrival_rates_dict = arrival_rates.to_json()
        arrival_rates_from_json = ArrivalRates.from_json(arrival_rates_dict=arrival_rates_dict)
        self.assertDictEqual(arrival_rates_dict, arrival_rates_from_json.to_json())
