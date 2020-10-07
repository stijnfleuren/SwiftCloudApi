from __future__ import annotations  # allows using ArrivalRates-typing inside ArrivalRates-class

from typing import Dict, List

from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


class QueueLengths:
    """Arrival rates of all traffic lights"""
    def __init__(self, id_to_queue_lengths: Dict[str, List[float]]) -> None:
        """
        :param id_to_queue_lengths: mapping of signalgroup id to a list of queue lengths (in personal car equivalent)
        for the associated traffic lights (in signalgroup.traffic_lights);
        We include these queue lengths implicitly in the arrival rate of this queue: we assume that the traffic in
        the initial queue arrives (evenly spread) during the horizon.
        return: -
        """
        self.id_to_queue_lengths = id_to_queue_lengths

        # raises ValueError if validation does not succeed
        self._validate()

    def to_json(self):
        """get dictionary structure that can be stored as json with json.dumps()"""
        return self.id_to_queue_lengths

    def _validate(self) -> None:
        """ Validate input arguments of QueueLengths; raises ValueError if validation does not pass"""
        # validate structure of id_to_queue_lengths
        error_message = "id_to_queue_lengths should be a dictionary mapping from a signal group id (str) to " \
                        "a list of queue lengths (List[float])"
        if not isinstance(self.id_to_queue_lengths, dict):
            raise ValueError(error_message)
        for _id, rates in self.id_to_queue_lengths.items():
            if not isinstance(_id, str):
                raise ValueError(error_message)
            if not isinstance(rates, list):
                raise ValueError(error_message)
            for rate in rates:
                if not isinstance(rate, (float, int)):
                    raise ValueError(error_message)

    @staticmethod
    def from_json(queue_lengths_dict) -> QueueLengths:
        """Loading arrival rates from json (expected same json structure as generated with to_json)"""
        return QueueLengths(id_to_queue_lengths=queue_lengths_dict)

    def __truediv__(self, time: float) -> ArrivalRates:
        """ divide the queue length by a time interval ('other' in hours) to get a rate in PCE/h"""
        if not isinstance(time, (int, float)):
            raise ArithmeticError("can divide queue_lengths rates only by float")
        id_to_arrival_rates = {id_: [rate/time for rate in rates] for id_, rates in self.id_to_queue_lengths.items()}
        return ArrivalRates(id_to_arrival_rates=id_to_arrival_rates)
