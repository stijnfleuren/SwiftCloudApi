import unittest
from typing import Dict

from swift_cloud_py.entities.control_output.phase_diagram import GreenYellowPhase, Phase, PhaseDiagram


class TestGreenYellowPhaseInputValidation(unittest.TestCase):

    def test_correct_input(self):
        """ Test initialization is correct with correct input"""
        # WHEN
        gy_phase = GreenYellowPhase(signalgroup_id="sg", interval_index=0)

        # THEN
        self.assertEqual(gy_phase.signalgroup_id, "sg")
        self.assertEqual(gy_phase.interval_index, 0)

    def test_id_no_string(self):
        """ Test id is converted to string """
        # WHEN
        # noinspection PyTypeChecker
        greenyellow_phase = GreenYellowPhase(signalgroup_id=1, interval_index=0)

        # THEN signalgroup_id should be converted to string
        self.assertIsInstance(greenyellow_phase.signalgroup_id, str)

    def test_index_no_int(self):
        """ Test constructing object fails if the index has the wrong datatype"""
        with self.assertRaises(ValueError):
            # WHEN
            # noinspection PyTypeChecker
            GreenYellowPhase(signalgroup_id="sg1", interval_index="wrong")

            # THEN an error should be raised


class TestPhaseInputValidation(unittest.TestCase):

    def test_correct_input(self):
        """ Test initialization is correct with correct input"""
        # WHEN
        phase = Phase(greenyellow_phases=[GreenYellowPhase(signalgroup_id="sg1", interval_index=1),
                                          GreenYellowPhase(signalgroup_id="sg2", interval_index=0)])

        # THEN
        self.assertEqual(phase.greenyellow_phases[0].signalgroup_id, "sg1")
        self.assertEqual(phase.greenyellow_phases[1].signalgroup_id, "sg2")
        self.assertEqual(phase.greenyellow_phases[0].interval_index, 1)
        self.assertEqual(phase.greenyellow_phases[1].interval_index, 0)

    def test_input_no_list(self):
        """ Test wrong input type (not a list)"""
        with self.assertRaises(ValueError):
            # WHEN
            # noinspection PyTypeChecker
            Phase(greenyellow_phases=1)

            # THEN an error should be raised

    def test_input_no_correct_list(self):
        """ Test wrong input type (not a list of GreenYellowPhase-objects)"""
        with self.assertRaises(ValueError):
            # WHEN
            # noinspection PyTypeChecker
            Phase(greenyellow_phases=[1, 2, 3])

            # THEN an error should be raised


class TestPhaseDiagramInputValidation(unittest.TestCase):

    @staticmethod
    def get_default_inputs() -> Dict:
        """ Function to get default (valid) inputs for GreenYellowInterval() """
        return dict(phases=[Phase(greenyellow_phases=[GreenYellowPhase(signalgroup_id="sg1", interval_index=1),
                                                      GreenYellowPhase(signalgroup_id="sg2", interval_index=0)]),
                            Phase(greenyellow_phases=[GreenYellowPhase(signalgroup_id="sg1", interval_index=1),
                                                      GreenYellowPhase(signalgroup_id="sg2", interval_index=0)]
                                  )])

    def test_successful_validation(self) -> None:
        """ Test initializing GreenYellowInterval object with correct input """
        # GIVEN
        input_dict = TestPhaseDiagramInputValidation.get_default_inputs()

        # WHEN
        PhaseDiagram(**input_dict)

        # THEN no error should be raised

    def test_input_no_list(self):
        """ Test wrong input type (not a list)"""
        with self.assertRaises(ValueError):
            # WHEN
            # noinspection PyTypeChecker
            PhaseDiagram(phases=1)

            # THEN an error should be raised

    def test_input_no_correct_list(self):
        """ Test wrong input type (not a list of GreenYellowPhase-objects)"""
        with self.assertRaises(ValueError):
            # WHEN
            # noinspection PyTypeChecker
            PhaseDiagram(phases=1)

            # THEN an error should be raised


class TestFTSJsonConversion(unittest.TestCase):

    def test_json_back_and_forth(self) -> None:
        """ test converting back and forth from and to json """
        # GIVEN
        input_dict = TestPhaseDiagramInputValidation.get_default_inputs()

        # WHEN
        phase_diagram = PhaseDiagram(**input_dict)

        # THEN converting back and forth should in the end give the same result
        phase_lists = phase_diagram.to_json()
        phase_diagram_from_json = PhaseDiagram.from_json(phase_lists=phase_lists)
        self.assertListEqual(phase_lists, phase_diagram_from_json.to_json())
