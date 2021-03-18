import unittest
from itertools import product
from typing import Dict

from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.sg_relations import Conflict, SyncStart, Offset, GreenyellowLead
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight


class TestInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ Function to get default (valid) inputs for Intersection() """
        signalgroups = [SignalGroup(id=f"sg{i+1}", traffic_lights=[TrafficLight(capacity=1800, lost_time=1)],
                                    min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80) for i in range(5)]
        conflicts = [Conflict(id1="sg1", id2="sg2", setup12=1, setup21=2)]
        sync_starts = [SyncStart(from_id="sg1", to_id="sg3")]
        offsets = [Offset(from_id="sg1", to_id="sg4", seconds=10)]
        greenyellow_leads = [GreenyellowLead(from_id="sg1", to_id="sg5", min_seconds=1, max_seconds=10)]
        return dict(signalgroups=signalgroups, conflicts=conflicts, sync_starts=sync_starts,
                    offsets=offsets, greenyellow_leads=greenyellow_leads)

    def test_successful_validation(self) -> None:
        """ Test initializing Intersection object with correct input """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        Intersection(**input_dict)

        # THEN no exception should occur

    def test_wrong_type(self) -> None:
        """ Test providing the wrong type of arguments (no list)"""

        # WHEN an input contains the wrong data type
        for key in TestInputValidation.get_default_inputs():
            with self.subTest(f"Wrong type in input '{key}'"):
                # GIVEN
                input_dict = TestInputValidation.get_default_inputs()
                input_dict[key] = 10  # wrong type (not a list)
                with self.assertRaises(TypeError):
                    # WHEN initializing the intersection
                    Intersection(**input_dict)

                    # THEN an error should be raised

    def test_wrong_type_in_list(self) -> None:
        """ Test providing the wrong type of elements inside the arguments (which are lists) """

        for key in TestInputValidation.get_default_inputs():
            with self.subTest(f"Wrong type in input '{key}'"):
                # GIVEN
                input_dict = TestInputValidation.get_default_inputs()
                input_dict[key].append(10)  # add other object (of wrong type) to the list
                with self.assertRaises(TypeError):
                    # WHEN initializing the intersection
                    Intersection(**input_dict)

                    # THEN an error should be raised

    def test_ids_not_unique(self) -> None:
        """ Test for multiple signal groups having the same id """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN an id is used twice
        input_dict["signalgroups"][-1].id = "sg1"  # other object (of wrong type) to the list
        with self.assertRaises(ValueError):
            Intersection(**input_dict)

            # THEN an error should be raised

    def test_unknown_ids(self) -> None:
        """ Test unknown ids being used in relations between signal groups """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN an unknown id is used in a relations between signal groups
        for key in ["conflicts", "sync_starts", "offsets", "greenyellow_leads"]:
            if key == "conflicts":
                input_dict[key][0].id1 = "unknown"
            else:
                input_dict[key][0].from_id = "unknown"
            with self.subTest(f"Unknown id used in input '{key}'"):
                with self.assertRaises(ValueError):
                    Intersection(**input_dict)

                    # THEN an error should be raised

    def test_multiple_relations(self) -> None:
        """ Test multiple relations being provided for the same pair of signal groups """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN two signal group relations exist for the same signal group pair
        id1 = "new_id1"
        id2 = "new_id2"
        for key1, key2 in product(["conflicts", "sync_starts", "offsets", "greenyellow_leads"],
                                  ["conflicts", "sync_starts", "offsets", "greenyellow_leads"]):
            if key1 == key2:
                continue

            if key1 == "conflicts":
                input_dict[key1][0].id1 = id1
                input_dict[key1][0].id2 = id2
            else:
                input_dict[key1][0].from_id = id2
                input_dict[key1][0].to_id = id1

            if key2 == "conflicts":
                input_dict[key2][0].id1 = id1
                input_dict[key2][0].id2 = id2
            else:
                input_dict[key2][0].from_id = id2
                input_dict[key2][0].to_id = id1

            with self.subTest(f"Two relations ('{key1}' and '{key2}') for same signalgroup pair"):
                with self.assertRaises(ValueError):
                    Intersection(**input_dict)

                    # THEN an error should be raised

    def test_setup_to_small(self) -> None:
        """ Test for setup time being too small """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN setup12 plus min_greenyellow of signal group sg1 is not strictly positive
        for setup12 in [-10, -11]:  # equal to min_greenyellow or even smaller
            with self.subTest(f"setup too small: '{setup12}'"):
                input_dict["conflicts"][0].setup12 = setup12
                with self.assertRaises(ValueError):
                    Intersection(**input_dict)

            # THEN an error should be raised


class TestGettingSignalGroup(unittest.TestCase):
    """Test retrieving signal group by id from intersection object"""

    def test_getting_signal_group(self):
        """ Test retrieving signal group by id """
        # GIVEN
        signalgroup1 = SignalGroup(id="sg1", traffic_lights=[TrafficLight(capacity=1800, lost_time=1)],
                                   min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)
        signalgroup2 = SignalGroup(id="sg2", traffic_lights=[TrafficLight(capacity=1800, lost_time=1)],
                                   min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)

        intersection = Intersection(signalgroups=[signalgroup1, signalgroup2], conflicts=[], sync_starts=[],
                                    offsets=[], greenyellow_leads=[])

        # WHEN/THEN
        self.assertEqual(intersection.get_signalgroup(signalgroup_id="sg1"), signalgroup1)
        self.assertEqual(intersection.get_signalgroup(signalgroup_id="sg2"), signalgroup2)

    def test_getting_non_existing_signal_group(self):
        """ Test retrieving signal group by id when this id does not exist """
        # GIVEN
        signalgroup1 = SignalGroup(id="sg1", traffic_lights=[TrafficLight(capacity=1800, lost_time=1)],
                                   min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)
        signalgroup2 = SignalGroup(id="sg2", traffic_lights=[TrafficLight(capacity=1800, lost_time=1)],
                                   min_greenyellow=10, max_greenyellow=80, min_red=10, max_red=80)
        intersection = Intersection(signalgroups=[signalgroup1, signalgroup2], conflicts=[], sync_starts=[],
                                    offsets=[], greenyellow_leads=[])

        with self.assertRaises(ValueError):
            # WHEN
            intersection.get_signalgroup(signalgroup_id="sg3")

            # THEN an error should be raised


class TestOtherRelations(unittest.TestCase):
    def test_other_relations(self) -> None:
        """ Test if the attribute other_relation containers all other relations (sync starts,
         offsets and greenyellow-leads)"""
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN an unknown id is used in a relations between signal groups
        intersection = Intersection(**input_dict)

        other_relations = intersection.other_relations
        # THEN other_relations is the list of all sync_starts, offsets and greenyellow-leads
        self.assertEqual(len(input_dict["sync_starts"]) + len(input_dict["offsets"]) +
                         len(input_dict["greenyellow_leads"]), len(other_relations))
        for key in ["sync_starts", "offsets", "greenyellow_leads"]:
            with self.subTest(f"'{key}' in other_relations"):
                for other_relation in input_dict[key]:
                    self.assertIn(other_relation, other_relations)


class TestJsonConversion(unittest.TestCase):
    def test_json_back_and_forth(self) -> None:
        """ Test converting back and forth from and to json """
        # GIVEN
        input_dict = TestInputValidation.get_default_inputs()

        # WHEN
        intersection = Intersection(**input_dict)

        # THEN converting back and forth should in the end give the same result
        intersection_dict = intersection.to_json()
        intersection_from_json = Intersection.from_json(intersection_dict=intersection_dict)
        self.assertDictEqual(intersection_dict, intersection_from_json.to_json())
