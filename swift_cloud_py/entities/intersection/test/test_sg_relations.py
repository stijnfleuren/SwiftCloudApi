import unittest
from typing import Dict

from swift_cloud_py.entities.intersection.sg_relations import Conflict


class TestConflictInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ function to get default (valid) inputs for SignalGroup() """
        return dict(id1="id1", id2="id2", setup12=1, setup21=2)

    def test_successful_validation(self) -> None:
        """ Test initializing Conflict object with correct input """
        # GIVEN
        input_dict = TestConflictInputValidation.get_default_inputs()

        # WHEN
        Conflict(**input_dict)

        # THEN no exception should occur

    def test_wrong_datatype_for_ids(self) -> None:
        """ Test giving wrong datatype to Conflict for ids """
        # GIVEN
        input_dict = TestConflictInputValidation.get_default_inputs()
        input_dict["id1"] = 1
        input_dict["id2"] = 2
        # WHEN initializing the signal group
        conflict = Conflict(**input_dict)

        # Should not give an error (datatype is converted to string)
        self.assertEqual(conflict.id1, "1")
        self.assertEqual(conflict.id2, "2")

    def test_wrong_datatype_for_numbers(self) -> None:
        """ Test giving wrong datatype to Conflict for numbers """
        for key in ["setup12", "setup21"]:
            with self.subTest(f"Wrong type in input '{key}'"):
                # GIVEN
                input_dict = TestConflictInputValidation.get_default_inputs()
                input_dict[key] = 'string'  # all arguments are numbers
                with self.assertRaises(ValueError):
                    Conflict(**input_dict)
