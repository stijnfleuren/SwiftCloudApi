import unittest
from typing import Dict

from swift_cloud_py.entities.intersection.traffic_light import TrafficLight


class TestInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ Function to get default (valid) inputs for TrafficLight() """
        return dict(capacity=1800, lost_time=1, weight=1, max_saturation=1)

    def test_successful_validation(self) -> None:
        """ Test initializing TrafficLight object with correct input """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        TrafficLight(**input_dict)

        # THEN no exception should occur

    def test_wrong_type(self) -> None:
        """ Test providing the wrong type """

        for key in TestInputValidation.get_default_inputs():
            with self.subTest(f"Wrong type in input '{key}'"):
                # GIVEN
                input_dict = TestInputValidation.get_default_inputs()
                input_dict[key] = 'string'  # all arguments are numbers
                with self.assertRaises(ValueError):
                    # WHEN initializing the traffic light
                    TrafficLight(**input_dict)

                    # THEN an error should be raised

    def test_negativity(self) -> None:
        """ Test providing negative values for capacity, lost_time, weight and max_saturation"""

        for key in TestInputValidation.get_default_inputs():
            with self.subTest(f"Wrong type in input '{key}'"):
                # GIVEN
                input_dict = TestInputValidation.get_default_inputs()
                input_dict[key] = -0.1  # all arguments are non-negative numbers
                with self.assertRaises(AssertionError):
                    # WHEN initializing the traffic light
                    TrafficLight(**input_dict)

                    # THEN an error should be raised

    def test_zero(self) -> None:
        """ Test providing zero values for capacity and max_saturation """

        for key in ["capacity", "max_saturation"]:
            with self.subTest(f"Wrong type in input '{key}'"):
                # GIVEN
                input_dict = TestInputValidation.get_default_inputs()
                input_dict[key] = 0.0  # argument should be positive
                with self.assertRaises(AssertionError):
                    # WHEN initializing the traffic light
                    TrafficLight(**input_dict)

                    # THEN an error should be raised


class TestJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ Test converting back and forth from and to json """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        traffic_light = TrafficLight(**input_dict)

        # THEN converting back and forth should in the end give the same result
        traffic_light_dict = traffic_light.to_json()
        traffic_light_from_json = TrafficLight.from_json(traffic_light_dict=traffic_light_dict)
        self.assertDictEqual(traffic_light_dict, traffic_light_from_json.to_json())
