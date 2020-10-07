import unittest
from typing import Dict

from swift_cloud_py.entities.intersection.sg_relations import Conflict, SyncStart, Coordination, PreStart


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
        with self.assertRaises(ValueError):
            Conflict(**input_dict)

        # THEN an error should be raised

    def test_setup_sum_negative(self) -> None:
        """ Test sum of setups being negative """
        # GIVEN
        input_dict = TestConflictInputValidation.get_default_inputs()
        input_dict["setup12"] = 0
        input_dict["setup21"] = -1
        with self.assertRaises(ValueError):
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
        """ Test giving wrong datatype to SyncStart for ids """
        # GIVEN
        input_dict = TestSyncStartInputValidation.get_default_inputs()
        input_dict["from_id"] = 1
        input_dict["to_id"] = 2

        # WHEN initializing the synchronous start
        sync_start = SyncStart(**input_dict)

        # Should not give an error (datatype is converted to string); note that from_id and to_id might have swapped;
        # this is done to store this SyncStart in an unambiguous manner.
        self.assertSetEqual({sync_start.from_id, sync_start.to_id}, {"1", "2"})

    def test_non_unique_ids(self) -> None:
        """ Test giving two identical ids to initialize a SyncStart """
        # GIVEN
        input_dict = TestSyncStartInputValidation.get_default_inputs()
        input_dict["from_id"] = "1"
        input_dict["to_id"] = "1"
        with self.assertRaises(ValueError):
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


class TestCoordinationInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ function to get default (valid) inputs for Coordination() """
        return dict(from_id="1", to_id="2", coordination_time=10)

    def test_successful_validation(self) -> None:
        """ Test initializing Coordination object with correct input """
        # GIVEN
        input_dict = TestCoordinationInputValidation.get_default_inputs()

        # WHEN
        Coordination(**input_dict)

        # THEN no exception should occur

    def test_wrong_datatype_for_ids(self) -> None:
        """ Test giving wrong datatype to Coordionation for ids """
        # GIVEN
        input_dict = TestCoordinationInputValidation.get_default_inputs()
        input_dict["from_id"] = 1
        input_dict["to_id"] = 2

        # WHEN initializing the coordination
        coordination = Coordination(**input_dict)

        # Should not give an error (datatype is converted to string)
        self.assertEqual(coordination.from_id, "1")
        self.assertEqual(coordination.to_id, "2")

    def test_non_unique_ids(self) -> None:
        """ Test giving two identical ids to initialize a Coordination """
        # GIVEN
        input_dict = TestCoordinationInputValidation.get_default_inputs()
        input_dict["from_id"] = "1"
        input_dict["to_id"] = "1"
        with self.assertRaises(ValueError):
            Coordination(**input_dict)

        # THEN an error should be raised


class TestCoordinationJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestCoordinationInputValidation.get_default_inputs()

        # WHEN
        coordination = Coordination(**input_dict)

        # THEN converting back and forth should in the end give the same result
        coordination_dict = coordination.to_json()
        coordination_from_json = Coordination.from_json(coordination_dict=coordination_dict)
        self.assertDictEqual(coordination_dict, coordination_from_json.to_json())


class TestPreStartInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ function to get default (valid) inputs for Coordination() """
        return dict(from_id="1", to_id="2", min_prestart=10, max_prestart=15)

    def test_successful_validation(self) -> None:
        """ Test initializing PreStart object with correct input """
        # GIVEN
        input_dict = TestPreStartInputValidation.get_default_inputs()

        # WHEN
        PreStart(**input_dict)

        # THEN no exception should occur

    def test_wrong_datatype_for_ids(self) -> None:
        """ Test giving wrong datatype to PreStart for ids """
        # GIVEN
        input_dict = TestPreStartInputValidation.get_default_inputs()
        input_dict["from_id"] = 1
        input_dict["to_id"] = 2

        # WHEN initializing the prestart
        prestart = PreStart(**input_dict)

        # Should not give an error (datatype is converted to string)
        self.assertEqual(prestart.from_id, "1")
        self.assertEqual(prestart.to_id, "2")

    def test_non_unique_ids(self) -> None:
        """ Test giving two identical ids to initialize a Coordination """
        # GIVEN
        input_dict = TestPreStartInputValidation.get_default_inputs()
        input_dict["from_id"] = "1"
        input_dict["to_id"] = "1"
        with self.assertRaises(ValueError):
            PreStart(**input_dict)

        # THEN an error should be raised

    def test_minimum_exceeding_maximum(self) -> None:
        """ Test giving two identical ids to initialize a Coordination """
        # GIVEN
        input_dict = TestPreStartInputValidation.get_default_inputs()
        input_dict["min_prestart"] = 20
        input_dict["max_prestart"] = 10
        with self.assertRaises(ValueError):
            PreStart(**input_dict)

        # THEN an error should be raised


class TestPreStartJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestPreStartInputValidation.get_default_inputs()

        # WHEN
        prestart = PreStart(**input_dict)

        # THEN converting back and forth should in the end give the same result
        prestart_dict = prestart.to_json()
        prestart_from_json = PreStart.from_json(pre_start_dict=prestart_dict)
        self.assertDictEqual(prestart_dict, prestart_from_json.to_json())
