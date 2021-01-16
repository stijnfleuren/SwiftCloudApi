from __future__ import annotations  # allows using a class as typing inside the same class
from typing import Dict


class Conflict:
    def __init__(self, id1: str, id2: str, setup12: float, setup21: float) -> None:
        """
        A conflict between two signal groups; this indicates that the corresponding traffic streams are conflicting and
        may not simultaneously cross the intersection.
        :param id1: id of signal group
        :param id2: id of signal group
        :param setup12: minimum time between the end of a greenyellow interval of signal group id1 and the start of
        a greenyellow interval of signal group id2.
        :param setup21: minimum time between the end of a greenyellow interval of signal group id2 and the start of
        a greenyellow interval of signal group id1.
        """
        # by converting to the correct data type we ensure correct types are used
        self.id1 = str(id1)
        self.id2 = str(id2)
        self.setup12 = float(setup12)  # defined as time from end gy of sg with id1 to start gy of sg with id2
        self.setup21 = float(setup21)

        # validate values of arguments
        self._validate()

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

    def _validate(self):
        """ Validate input arguments of Confict """
        if not self.id1 != self.id2:
            raise ValueError("ids of conflict must be different")
        if not self.setup12 + self.setup21 >= 0:
            raise ValueError("setup12+setup21 must be non-negative")


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

        self._validate()

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

    def _validate(self):
        """ Validate input arguments of SyncStart """
        if not self.from_id != self.to_id:
            raise ValueError("ids of sync-start must be different")


class Offset:
    def __init__(self, from_id: str, to_id: str, seconds: float) -> None:
        """
        Force an offset of 'offset' seconds between the start (of each greenyellow interval) of
        signalgroup with id 'from_id' and the start (of each greenyellow interval) of the signalgroup with id 'to_id'.
        (the ones with id 'from_id' and 'to_id').
        :param from_id: name of signalgroup
        :param to_id: name of signalgroup
        :param seconds: The exact number of seconds forced between the start of the greenyellow interval of
        signal group 'from_id' to the greenyellow interval of signal group 'to_id'

        Note: This also forces the number of greenyellow intervals to be the same for both signal groups
        """
        # by converting to the correct data type we ensure correct types are used
        self.from_id = str(from_id)
        self.to_id = str(to_id)
        self.seconds = float(seconds)

        # validate values of arguments
        self._validate()

    def to_json(self) -> Dict:
        """get dictionary structure that can be stored as json with json.dumps()"""
        return {"from_id": self.from_id, "from_start_gy": True,
                "to_id": self.to_id, "to_start_gy": True,
                "min_time": self.seconds, "max_time": self.seconds, "same_start_phase": False}

    @staticmethod
    def from_json(offset_dict: Dict) -> Offset:
        """Loading offset from json (expected same json structure as generated with to_json)"""
        assert offset_dict["min_time"] == offset_dict["max_time"], \
            "trying to load Offset from dictionary, but the provided dictionary is not an offset!"
        return Offset(from_id=offset_dict["from_id"],
                      to_id=offset_dict["to_id"],
                      seconds=offset_dict["min_time"])

    def _validate(self):
        """ Validate input arguments of Offset """
        if not self.from_id != self.to_id:
            raise ValueError("ids of offset must be different")


class PreStart:
    def __init__(self, from_id: str, to_id: str, min_seconds: float, max_seconds: float) -> None:
        """
        A prestart is the time from signal group "from_id" starting its greenyellow interval to signal group "to_id"
        starting its greenyellow interval; for example a prestart of at least 5 seconds and at most 10 seconds
        of sg28 with regards to sg1 means that sg28 must start its greenyellow interval
        at least 5 seconds and at most 10 seconds before SG1 starts it greenyellow interval.
        :param from_id:
        :param to_id:
        :param min_seconds: lower bound on the allowed duration of the prestart
        :param max_seconds: upper bound on the allowed duration of the prestart
        """
        # by converting to the correct data type we ensure correct types are used
        self.from_id = str(from_id)
        self.to_id = str(to_id)
        self.min_prestart = float(min_seconds)
        self.max_prestart = float(max_seconds)

        # validate values of arguments
        self._validate()

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
                        min_seconds=pre_start_dict["min_time"],
                        max_seconds=pre_start_dict["max_time"])

    def _validate(self):
        """ Validate input arguments of PreStart """
        if not self.from_id != self.to_id:
            raise ValueError("ids of PreStart must be different")

        if not self.max_prestart >= self.min_prestart:
            raise ValueError("max_prestart should exceed (or equal) min_prestart")
