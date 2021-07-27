import unittest
from typing import Dict

from swift_cloud_py.entities.intersection.periodic_order import PeriodicOrder


class TestPeriodicOrderInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ function to get default (valid) inputs for PeriodicOrder() """
        return {"order": ["sg1", "sg2", "sg3"]}

    def test_successful_validation(self) -> None:
        """ Test initializing PeriodicOrder object with correct input """
        # GIVEN
        input_dict = TestPeriodicOrderInputValidation.get_default_inputs()

        # WHEN
        PeriodicOrder(**input_dict)

        # THEN no exception should occur

    def test_duplicate_ids(self) -> None:
        """ Test that an error is raised when the same id is used multiple times """
        # GIVEN
        input_dict = TestPeriodicOrderInputValidation.get_default_inputs()
        input_dict["order"].append("sg1")
        # WHEN initializing the periodic order
        with self.assertRaises(ValueError):
            PeriodicOrder(**input_dict)


class TestPeriodicOrderJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestPeriodicOrderInputValidation.get_default_inputs()

        # WHEN
        periodic_order = PeriodicOrder(**input_dict)

        # THEN converting back and forth should in the end give the same result
        periodic_order_dict = periodic_order.to_json()
        periodic_order_from_json = PeriodicOrder.from_json(order_dict=periodic_order_dict)
        self.assertDictEqual(periodic_order_dict, periodic_order_from_json.to_json())