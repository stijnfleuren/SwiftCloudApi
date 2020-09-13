from __future__ import annotations  # allows using ArrivalRates-typing inside ArrivalRates-class

from typing import Dict, List


class QueueLengths:
    """Arrival rates of all traffic lights"""
    def __init__(self, id_to_queue_lengths: Dict[str, List[float]]) -> None:
        """
        :param id_to_queue_lengths: mapping of signalgroup id to a list of queue lengths (in personal car equivalent)
        for the associated traffic lights (in signalgroup.traffic_lights)
        return: -
        """
        self.id_to_queue_lengths = id_to_queue_lengths

    def to_json(self):
        """get dictionary structure that can be stored as json with json.dumps()"""
        return self.id_to_queue_lengths

    @staticmethod
    def from_json(queue_lengths_dict) -> QueueLengths:
        """Loading arrival rates from json (expected same json structure as generated with to_json)"""
        return QueueLengths(id_to_queue_lengths=queue_lengths_dict)
