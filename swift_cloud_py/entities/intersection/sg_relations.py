from __future__ import annotations  # allows using a class as typing inside the same class
from typing import Dict


class Conflict:
    def __init__(self, id1: str, id2: str, setup12: float, setup21: float) -> None:
        """
        A conflict between two signalgroups; this indicates that the corresponding traffic streams are conflicting and
        may not simultaneously cross the intersection.
        :param id1: id of signalgroup
        :param id2: id of signalgroup
        :param setup12: minimum time between the end of a greenyellow interval of signalgroup id1 and the start of
        a greenyellow interval of signalgroup id2.
        :param setup21: minimum time between the end of a greenyellow interval of signalgroup id2 and the start of
        a greenyellow interval of signalgroup id1.
        """
        assert setup12 + setup21 >= 0
        # by converting to the correct data type we ensure correct types are used
        self.id1 = str(id1)
        self.id2 = str(id2)
        self.setup12 = float(setup12)  # defined as time from end gy of sg with id1 to start gy of sg with id2
        self.setup21 = float(setup21)

    def to_json(self) -> Dict:
        """get dictionary structure that can be stored as json with json.dumps()"""
        return self.__dict__

    @staticmethod
    def from_json(conflict_dict: Dict) -> Conflict:
        """Loading conflict from json (expected same json structure as generated with to_json)"""
        return Conflict(id1=conflict_dict["id1"],
                        id2=conflict_dict["id2"],
                        setup12=conflict_dict["setup12"],
                        setup21=conflict_dict["setup21"])


class SyncStart:
    def __init__(self, from_id: str, to_id: str) -> None:
        """
        Force synchronous start (of each greenyellow interval)
        between two signal groups (the ones with id 'from_id' and 'to_id').

        Note: This also forces the number of greenyellow intervals to be the same for both signal groups
        :param from_id: name of signalgroup
        :param to_id: name of signalgroup
        """
        # by converting to the correct data type we ensure correct types are used
        self.from_id = str(from_id)
        self.to_id = str(to_id)

        # store unambiguously
        if self.from_id < self.to_id:
            self.to_id, self.from_id = self.from_id, self.to_id

    def to_json(self) -> Dict:
        """get dictionary structure that can be stored as json with json.dumps()"""
        return {"from_id": self.from_id, "from_start_gy": True,
                "to_id": self.to_id, "to_start_gy": True,
                "min_time": 0.0, "max_time": 0.0, "same_start_phase": True}

    @staticmethod
    def from_json(sync_start_dict: Dict) -> SyncStart:
        """Loading synchronous start from json (expected same json structure as generated with to_json)"""
        assert sync_start_dict["min_time"] == sync_start_dict["max_time"] == 0, \
            "trying to load SyncStart from dictionary, but the provided dictionary is not a synchronous start!"
        return SyncStart(from_id=sync_start_dict["from_id"],
                         to_id=sync_start_dict["to_id"])


class Coordination:
    def __init__(self, from_id: str, to_id: str, coordination_time: float) -> None:
        """
        Force coordination between the start (of each greenyellow interval) of two signalgroups
        (the ones with id 'from_id' and 'to_id').
        :param from_id: name of signalgroup
        :param to_id: name of signalgroup
        :param coordination_time: The exact number of seconds forced between the start of the greenyellow interval of
        signal group 'from_id' to the greenyellow interval of signal group 'to_id'

        Note: This also forces the number of greenyellow intervals to be the same for both signal groups
        """
        # by converting to the correct data type we ensure correct types are used
        self.from_id = str(from_id)
        self.to_id = str(to_id)
        self.coordination_time = float(coordination_time)

    def to_json(self) -> Dict:
        """get dictionary structure that can be stored as json with json.dumps()"""
        return {"from_id": self.from_id, "from_start_gy": True,
                "to_id": self.to_id, "to_start_gy": True,
                "min_time": self.coordination_time, "max_time": self.coordination_time, "same_start_phase": False}

    @staticmethod
    def from_json(coordination_dict: Dict) -> Coordination:
        """Loading coordination from json (expected same json structure as generated with to_json)"""
        assert coordination_dict["min_time"] == coordination_dict["max_time"], \
            "trying to load Coordination from dictionary, but the provided dictionary is not a coordination!"
        return Coordination(from_id=coordination_dict["from_id"],
                            to_id=coordination_dict["to_id"],
                            coordination_time=coordination_dict["min_time"])


class PreStart:
    def __init__(self, from_id: str, to_id: str, min_prestart: float, max_prestart: float) -> None:
        """
        A prestart is the time from signal group "from_id" starting its greenyellow interval to signal group "to_id"
        starting its greenyellow interval; for example a prestart of at least 5 seconds and at most 10 seconds
        of sg28 with regards to sg1 means that sg28 must start its greenyellow interval
        at least 5 seconds and at most 10 seconds before SG1 starts it greenyellow interval.
        :param from_id:
        :param to_id:
        :param min_prestart: lower bound on the allowed duration of the prestart
        :param min_prestart: upper bound on the allowed duration of the prestart
        """
        # by converting to the correct data type we ensure correct types are used
        self.from_id = str(from_id)
        self.to_id = str(to_id)
        self.min_prestart = float(min_prestart)
        self.max_prestart = float(max_prestart)

    def to_json(self) -> Dict:
        """get dictionary structure that can be stored as json with json.dumps()"""
        return {"from_id": self.from_id, "from_start_gy": True,
                "to_id": self.to_id, "to_start_gy": True,
                "min_time": self.min_prestart, "max_time": self.max_prestart,
                "same_start_phase": True}

    @staticmethod
    def from_json(pre_start_dict: Dict) -> PreStart:
        """Loading prestart from json (expected same json structure as generated with to_json)"""
        return PreStart(from_id=pre_start_dict["from_id"],
                        to_id=pre_start_dict["to_id"],
                        min_prestart=pre_start_dict["min_time"],
                        max_prestart=pre_start_dict["max_time"])
