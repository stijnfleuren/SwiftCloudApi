import unittest
from typing import Dict

from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates
from swift_cloud_py.entities.scenario.queue_lengths import QueueLengths


class TestInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ Function to get default (valid) inputs for QueueLengths() """
        return dict(id_to_queue_lengths={"1": [1000, 950], "2": [850, 700]})

    def test_successful_validation(self) -> None:
        """ Test initializing QueueLengths object with correct input """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        QueueLengths(**input_dict)

        # THEN no error should be raised

    def test_no_dict(self) -> None:
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id_to_queue_lengths"] = 1

        with self.assertRaises(AssertionError):
            # WHEN initializing the queue lengths
            QueueLengths(**input_dict)

            # THEN an error should be raised

    def test_no_string_values(self) -> None:
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id_to_queue_lengths"][1] = [1, 2]  # add value (1) which is not a string

        with self.assertRaises(AssertionError):
            # WHEN initializing the queue lengths
            QueueLengths(**input_dict)

            # THEN an error should be raised

    def test_no_list_for_rates(self) -> None:
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id_to_queue_lengths"]["3"] = 1  # rates is not a list

        with self.assertRaises(AssertionError):
            # WHEN initializing the queue lengths
            QueueLengths(**input_dict)

            # THEN an error should be raised

    def test_queue_lengths_no_number(self) -> None:
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id_to_queue_lengths"]["3"] = [1, "3"]  # rates is not a list of numbers

        with self.assertRaises(AssertionError):
            # WHEN initializing the queue lengths
            QueueLengths(**input_dict)

            # THEN an error should be raised


class TestOperations(unittest.TestCase):

    def test_divide(self) -> None:
        """ Test dividing QueueLengths by a float (a time)"""
        # GIVEN
        queue_lengths = QueueLengths(id_to_queue_lengths={"1": [1000, 950], "2": [850, 700]})

        # WHEN
        rates = queue_lengths / 2

        # THEN
        self.assertIsInstance(rates, ArrivalRates)
        self.assertListEqual(rates.id_to_arrival_rates["1"], [1000 / 2, 950 / 2])
        self.assertListEqual(rates.id_to_arrival_rates["2"], [850 / 2, 700 / 2])

    def test_dividing_no_float(self) -> None:
        """ Test dividing by incorrect datatype """
        # GIVEN
        queue_lengths = QueueLengths(id_to_queue_lengths={"1": [1000, 950], "2": [850, 700]})

        with self.assertRaises(AssertionError):
            # WHEN adding to rates with different ids
            queue_lengths / "str"

            # THEN an assertion should be raised


class TestJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        queue_lengths = QueueLengths(**input_dict)

        # THEN converting back and forth should in the end give the same result
        queue_lengths_dict = queue_lengths.to_json()
        queue_lengths_from_json = QueueLengths.from_json(queue_lengths_dict=queue_lengths_dict)
        self.assertDictEqual(queue_lengths_dict, queue_lengths_from_json.to_json())
