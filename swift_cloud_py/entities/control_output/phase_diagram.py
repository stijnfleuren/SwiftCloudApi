from __future__ import annotations  # allows using a class as typing inside the same class
from typing import List


def sort_by_name(name: str):
    """ function needed to sort signal groups by name """
    return len(name), name


class GreenYellowPhase:
    def __init__(self, signalgroup_id: str, interval_index: int) -> None:
        """
        Refers to the (interval_index + 1)th greenyellow interval of the signal group with id signalgroup_id
        :param signalgroup_id:
        :param interval_index:
        """
        # explicit type conversion ensures correct types are used
        self.signalgroup_id = str(signalgroup_id)
        self.interval_index = int(interval_index)

    def to_json(self) -> List:
        """get json-serializable structure that can be stored as json with json.dumps()"""
        return [self.signalgroup_id, self.interval_index]

    @staticmethod
    def from_json(json_list: List) -> GreenYellowPhase:
        """Loading greenyellow phase from json (expected same json structure as generated with to_json)"""
        return GreenYellowPhase(signalgroup_id=json_list[0], interval_index=json_list[1])

    def __str__(self):
        """string representation of object"""
        return f"(id={self.signalgroup_id}, k={self.interval_index})"


class Phase:
    def __init__(self, greenyellow_phases: List[GreenYellowPhase]) -> None:
        self.greenyellow_phases = greenyellow_phases

        self._validate()

    def to_json(self) -> List[List]:
        """get json-serializable structure that can be stored as json with json.dumps()"""
        return [greenyellow_phase.to_json() for greenyellow_phase in self.greenyellow_phases]

    @staticmethod
    def from_json(phase_list: List[List]) -> Phase:
        """Loading phase from json (expected same json structure as generated with to_json)"""
        return Phase(greenyellow_phases=[GreenYellowPhase.from_json(greenyellow_phase)
                                         for greenyellow_phase in phase_list])

    def _validate(self):
        """ Validate arguments of Phase object"""
        error_message = "greenyellow_phases should be a list of GreenYellowPhase-objects"
        if not isinstance(self.greenyellow_phases, list):
            raise ValueError(error_message)
        for greenyellow_phase in self.greenyellow_phases:
            if not isinstance(greenyellow_phase, GreenYellowPhase):
                raise ValueError(error_message)

    def __str__(self) -> str:
        """string representation of object"""
        string = "["
        # visualize in sorted (by name) order
        greenyellow_phases = sorted(self.greenyellow_phases,
                                    key=lambda _greenyellow_phase: sort_by_name(_greenyellow_phase.signalgroup_id))
        for index, greenyellow_phase in enumerate(greenyellow_phases):
            if index > 0:
                string += ", "
            string += str(greenyellow_phase)
        string += "]"
        return string


class PhaseDiagram:
    def __init__(self, phases: List[Phase]) -> None:
        self.phases = phases

        self._validate()

    def to_json(self) -> List[List[List]]:
        """get json_serializable structure that can be stored as json with json.dumps()"""
        return [phase.to_json() for phase in self.phases]

    @staticmethod
    def from_json(phase_lists: List[List[List]]) -> PhaseDiagram:
        """Loading phase diagram from json (expected same json structure as generated with to_json)"""
        return PhaseDiagram(phases=[Phase.from_json(phase_list=phase_list) for phase_list in phase_lists])

    def _validate(self):
        """ Validate arguments of PhaseDiagram object"""
        error_message = "phases should be a list of Phase-objects"
        if not isinstance(self.phases, list):
            raise ValueError(error_message)
        for phase in self.phases:
            if not isinstance(phase, Phase):
                raise ValueError(error_message)

    def __str__(self) -> str:
        """string representation of object"""
        string = f"phase diagram:"
        for phase in self.phases:
            string += "\n"
            string += f"\t{str(phase)}"
        return string
