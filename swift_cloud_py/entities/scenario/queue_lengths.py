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

        # validate structure of id_to_arrival_rates
        error_message = "id_to_queue_lengths should be a dictionary mapping from a signal group id (str) to " \
                        "a list of queue_lengths (List[float])"
        assert isinstance(id_to_queue_lengths, dict), error_message
        for _id, rates in id_to_queue_lengths.items():
            assert isinstance(_id, str), error_message
            assert isinstance(rates, list), error_message
            for rate in rates:
                assert isinstance(rate, (float, int)), error_message

    def to_json(self):
        """get dictionary structure that can be stored as json with json.dumps()"""
        return self.id_to_queue_lengths

    @staticmethod
    def from_json(queue_lengths_dict) -> QueueLengths:
        """Loading arrival rates from json (expected same json structure as generated with to_json)"""
        return QueueLengths(id_to_queue_lengths=queue_lengths_dict)

    def __truediv__(self, time: float) -> ArrivalRates:
        """ divide the queue length by a time interval ('other' in hours) to get a rate in PCE/h"""
        assert isinstance(time, (int, float)), "can divide queue_lengths rates only by float"
        id_to_arrival_rates = {id_: [rate/time for rate in rates] for id_, rates in self.id_to_queue_lengths.items()}
        return ArrivalRates(id_to_arrival_rates=id_to_arrival_rates)
