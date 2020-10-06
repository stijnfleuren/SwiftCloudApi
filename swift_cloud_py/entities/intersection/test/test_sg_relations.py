import unittest
from typing import Dict

from swift_cloud_py.entities.intersection.sg_relations import Conflict, SyncStart


class TestConflictInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ function to get default (valid) inputs for Conflict() """
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
        # WHEN initializing the conflict
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

                # THEN an error should be raised

    def test_non_unique_ids(self) -> None:
        """ Test giving two identical ids to initialize a Conflict """
        # GIVEN
        input_dict = TestConflictInputValidation.get_default_inputs()
        input_dict["id1"] = "1"
        input_dict["id2"] = "1"
        with self.assertRaises(AssertionError):
            Conflict(**input_dict)

        # THEN an error should be raised

    def test_setup_sum_negative(self) -> None:
        """ Test sum of setups being negative """
        # GIVEN
        input_dict = TestConflictInputValidation.get_default_inputs()
        input_dict["setup12"] = 0
        input_dict["setup21"] = -1
        with self.assertRaises(AssertionError):
            Conflict(**input_dict)

        # THEN an error should be raised


class TestConflictJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestConflictInputValidation.get_default_inputs()

        # WHEN
        conflict = Conflict(**input_dict)

        # THEN converting back and forth should in the end give the same result
        conflict_dict = conflict.to_json()
        conflict_from_json = Conflict.from_json(conflict_dict=conflict_dict)
        self.assertDictEqual(conflict_dict, conflict_from_json.to_json())


class TestSyncStartInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ function to get default (valid) inputs for SyncStart() """
        return dict(from_id="1", to_id="2")

    def test_successful_validation(self) -> None:
        """ Test initializing SyncStart object with correct input """
        # GIVEN
        input_dict = TestSyncStartInputValidation.get_default_inputs()

        # WHEN
        SyncStart(**input_dict)

        # THEN no exception should occur

    def test_wrong_datatype_for_ids(self) -> None:
        """ Test giving wrong SyncStart to Conflict for ids """
        # GIVEN
        input_dict = TestSyncStartInputValidation.get_default_inputs()
        input_dict["from_id"] = 1
        input_dict["to_id"] = 2

        # WHEN initializing the synchronous start
        sync_start = SyncStart(**input_dict)

        # Should not give an error (datatype is converted to string)
        self.assertEqual(sync_start.from_id, "1")
        self.assertEqual(sync_start.to_id, "2")

    def test_non_unique_ids(self) -> None:
        """ Test giving two identical ids to initialize a Conflict """
        # GIVEN
        input_dict = TestSyncStartInputValidation.get_default_inputs()
        input_dict["from_id"] = "1"
        input_dict["to_id"] = "1"
        with self.assertRaises(AssertionError):
            SyncStart(**input_dict)

        # THEN an error should be raised


class TestSyncStartJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestSyncStartInputValidation.get_default_inputs()

        # WHEN
        sync_start = SyncStart(**input_dict)

        # THEN converting back and forth should in the end give the same result
        sync_start_dict = sync_start.to_json()
        sync_start_from_json = SyncStart.from_json(sync_start_dict=sync_start_dict)
        self.assertDictEqual(sync_start_dict, sync_start_from_json.to_json())