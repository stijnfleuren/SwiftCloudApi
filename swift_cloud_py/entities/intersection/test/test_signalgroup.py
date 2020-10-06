import unittest
from typing import Dict

from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight


class TestInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ function to get default (valid) inputs for SignalGroup() """
        return dict(id="id1", traffic_lights=[TrafficLight(capacity=1800, lost_time=1)],
                    min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80, min_nr=1, max_nr=2)

    def test_successful_validation(self) -> None:
        """ test initializing SignalGroup object with correct input """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        SignalGroup(**input_dict)

        # THEN no exception should occur

    def test_id_not_str(self) -> None:
        """ test providing the wrong type of id"""

        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["id"] = 1  # not a string
        # WHEN initializing the signal grouip
        signalgroup = SignalGroup(**input_dict)

        # THEN should not raise an error, input is converted to string (if possible)
        self.assertEqual(signalgroup.id, "1")

    def test_wrong_type_numbers(self) -> None:
        """ test providing the wrong type for numeric arguments"""

        for key in ["min_greenyellow", "max_greenyellow", "min_red", "max_red", "min_nr", "max_nr"]:
            with self.subTest(f"Wrong type in input '{key}'"):
                # GIVEN
                input_dict = TestInputValidation.get_default_inputs()
                input_dict[key] = 'string'  # all arguments are numbers
                with self.assertRaises(ValueError):
                    # WHEN initializing the signal group
                    SignalGroup(**input_dict)

                    # THEN an error should be raised

    def test_float_instead_of_int(self) -> None:
        """ test providing float instead of int for min_nr and max_nr"""

        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["min_nr"] = 2.2
        input_dict["max_nr"] = 3.2
        # WHEN initializing the signal group
        signalgroup = SignalGroup(**input_dict)

        # THEN no error should be raised. The number is converted to an int:
        self.assertEqual(signalgroup.min_nr, 2)
        self.assertEqual(signalgroup.max_nr, 3)

    def test_min_nr_below_one(self):
        """ test min_nr being smaller than one"""
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["min_nr"] = 0

        with self.assertRaises(AssertionError):
            # WHEN initializing the signal group
            SignalGroup(**input_dict)

            # THEN an error should be raised

    def test_negativity(self) -> None:
        """ Test providing negative values for min_greenyellow, max_greenyellow, min_red, max_red, min_nr, max_nr """

        for key in ["min_greenyellow", "max_greenyellow", "min_red", "max_red", "min_nr", "max_nr"]:
            with self.subTest(f"Negative input for '{key}'"):
                # GIVEN
                input_dict = TestInputValidation.get_default_inputs()
                input_dict[key] = -0.1  # values should be non-negative
                with self.assertRaises(AssertionError):
                    # WHEN initializing the SignalGroup
                    SignalGroup(**input_dict)

                    # THEN an error should be raised

    def test_being_zero(self) -> None:
        """ Test providing zero values for max_greenyellow and max_red"""

        for key in ["max_greenyellow", "max_red"]:
            with self.subTest(f"Zero input for '{key}'"):
                # GIVEN
                input_dict = TestInputValidation.get_default_inputs()
                input_dict[key] = 0.0  # values should be non-negative
                with self.assertRaises(AssertionError):
                    # WHEN initializing the SignalGroup
                    SignalGroup(**input_dict)

                    # THEN an error should be raised

    def test_max_smaller_than_min(self) -> None:
        """ Test maximum value being smaller then minimum value, e.g., for maximum and minimum greenyellow times """

        for min_var, max_var in [("min_greenyellow", "max_greenyellow"), ("min_red", "max_red"), ("min_nr", "max_nr")]:
            with self.subTest(f"{max_var} smaller than {min_var}"):
                with self.assertRaises(AssertionError):
                    # GIVEN
                    input_dict = TestInputValidation.get_default_inputs()
                    input_dict[min_var] = 2.2  # all arguments are numbers
                    input_dict[max_var] = 1.2  # all arguments are numbers
                    # WHEN initializing the signalgroup
                    SignalGroup(**input_dict)

                    # THEN an error should be raised

    def test_wrong_type_for_traffic_lights(self) -> None:
        """ test providing the wrong type for traffic_lights (not a list)"""

        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["traffic_lights"] = "wrong type"  # all arguments are non-negative numbers
        with self.assertRaises(AssertionError):
            # WHEN initializing the signal group
            SignalGroup(**input_dict)

            # THEN an error should be raised

    def test_wrong_type_for_elements_of_traffic_lights(self) -> None:
        """ test providing the wrong type for traffic_lights (not a list)"""

        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()
        input_dict["traffic_lights"][0] = "wrong type"  # all arguments are non-negative numbers
        with self.assertRaises(AssertionError):
            # WHEN initializing the signal group
            SignalGroup(**input_dict)

            # THEN an error should be raised


class TestJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        signalgroup = SignalGroup(**input_dict)

        # THEN converting back and forth should in the end give the same result
        signalgroup_dict = signalgroup.to_json()
        signalgroup_from_json = SignalGroup.from_json(signalgroup_dict=signalgroup_dict)
        self.assertDictEqual(signalgroup_dict, signalgroup_from_json.to_json())
