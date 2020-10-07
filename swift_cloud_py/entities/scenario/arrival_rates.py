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

        # validate inputs
        self._validate()

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

    def _validate(self) -> None:
        """ Validate input arguments of ArrivalRates; raises ValueError if validation does not pass"""
        # validate structure of id_to_arrival_rates
        error_message = "id_to_arrival_rates should be a dictionary mapping from a signal group id (str) to " \
                        "a list of arrival rates (List[float])"
        if not isinstance(self.id_to_arrival_rates, dict):
            raise ValueError(error_message)
        for _id, rates in self.id_to_arrival_rates.items():
            if not isinstance(_id, str):
                raise ValueError(error_message)
            if not isinstance(rates, list):
                raise ValueError(error_message)
            for rate in rates:
                if not isinstance(rate, (float, int)):
                    raise ValueError(error_message)

    def __add__(self, other: ArrivalRates):
        """ add two arrival rates """
        if not isinstance(other, ArrivalRates):
            raise ArithmeticError("can only add ArrivalRates object to ArrivalRates")
        other_id_to_arrival_rates = other.id_to_arrival_rates

        # validate inputs
        other_ids = {_id for _id in other_id_to_arrival_rates}
        other_id_to_num_rates = {_id: len(rates) for _id, rates in other_id_to_arrival_rates.items()}
        ids = {_id for _id in self.id_to_arrival_rates}
        id_to_num_rates = {_id: len(rates) for _id, rates in self.id_to_arrival_rates.items()}
        if not ids == other_ids:
            raise ArithmeticError("when adding two ArrivalRates they should have the same ids")
        if not id_to_num_rates == other_id_to_num_rates:
            raise ArithmeticError("when adding two ArrivalRates all rates should have equal length")

        id_to_arrival_rates = \
            {id_: [rate + other_rate for rate, other_rate in zip(rates, other_id_to_arrival_rates[id_])]
             for id_, rates in self.id_to_arrival_rates.items()}
        return ArrivalRates(id_to_arrival_rates=id_to_arrival_rates)

    def __mul__(self, factor: float):
        """ Multiply the arrival rates with a factor """
        if not isinstance(factor, (float, int)):
            raise ArithmeticError("can only multiply ArrivalRates object with a float")
        id_to_arrival_rates = \
            {id_: [rate * factor for rate in rates] for id_, rates in self.id_to_arrival_rates.items()}
        return ArrivalRates(id_to_arrival_rates=id_to_arrival_rates)
