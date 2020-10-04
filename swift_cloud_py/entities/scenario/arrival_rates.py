from __future__ import annotations  # allows using ArrivalRates-typing inside ArrivalRates-class

import json
from typing import Dict, List


class ArrivalRates:
    """Arrival rates of all traffic lights"""
    def __init__(self, id_to_arrival_rates: Dict[str, List[float]]) -> None:
        """
        :param id_to_arrival_rates: mapping of signalgroup id to a list of arrival rates for the associated traffic
        lights (in signalgroup.traffic_lights)
        return: -
        """
        self.id_to_arrival_rates = id_to_arrival_rates

    def to_json(self):
        """get dictionary structure that can be stored as json with json.dumps()"""
        return self.id_to_arrival_rates

    @staticmethod
    def from_json(arrival_rates_dict) -> ArrivalRates:
        """Loading arrival rates from json (expected same json structure as generated with to_json)"""
        return ArrivalRates(id_to_arrival_rates=arrival_rates_dict)

    @staticmethod
    def from_swift_mobility_export(json_path) -> ArrivalRates:
        """
        Loading arrival rates from json-file exported from Swift Mobility Desktop
        :param json_path: path to json file
        :return: intersection object
        """
        with open(json_path, "r") as f:
            json_dict = json.load(f)

        return ArrivalRates.from_json(arrival_rates_dict=json_dict["arrival_rates"])

    def __add__(self, other: ArrivalRates):
        """ add two arrival rates """
        assert isinstance(other, ArrivalRates), "can only add ArrivalRates object to ArrivalRates"
        other_id_to_arrival_rates = other.id_to_arrival_rates
        id_to_arrival_rates = \
            {id_: [rate + other_rate for rate, other_rate in zip(rates, other_id_to_arrival_rates[id_])]
             for id_, rates in self.id_to_arrival_rates.items()}
        return ArrivalRates(id_to_arrival_rates=id_to_arrival_rates)

    def __mul__(self, factor: float):
        """ Multiply the arrival rates with a factor """
        assert isinstance(factor, (float, int)), "can only multiply ArrivalRates object with a float"
        id_to_arrival_rates = \
            {id_: [rate * factor for rate in rates] for id_, rates in self.id_to_arrival_rates.items()}
        return ArrivalRates(id_to_arrival_rates=id_to_arrival_rates)
