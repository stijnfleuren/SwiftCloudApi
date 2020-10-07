from __future__ import annotations  # allows using SignalGroup-typing inside SignalGroup-class

from typing import List, Dict

from swift_cloud_py.entities.intersection.traffic_light import TrafficLight


class SignalGroup:
    # noinspection PyShadowingBuiltins
    def __init__(self, id: str, traffic_lights: List[TrafficLight], min_greenyellow: float, max_greenyellow: float,
                 min_red: float,  max_red: float, min_nr: int = 1, max_nr: int = 1) -> None:
        """
        Representation of signal group, which is a group of traffic lights with the same state (green, yellow, red))
        :param id: name of the signal group
        :param traffic_lights: list of traffic lights that are part of this signal group
        :param min_greenyellow: minimum duration (in seconds) of each greenyellow interval
        :param max_greenyellow: maximum duration (in seconds) of each greenyellow interval
        :param min_red: minimum duration (in seconds) of each red interval
        :param max_red: maximum duration (in seconds) of each red interval
        :param min_nr: minimum number of greenyellow intervals (during a repeating period)
        :param max_nr: maximum number of greenyellow intervals (during a repeating period);
        the lower this value the faster the optimization!
        """
        # by converting to the correct type we already check for incompatible types
        self.id = str(id)
        self.min_greenyellow = float(min_greenyellow)
        self.max_greenyellow = float(max_greenyellow)
        self.min_red = float(min_red)
        self.max_red = float(max_red)
        self.traffic_lights = traffic_lights
        self.min_nr = int(min_nr)
        self.max_nr = int(max_nr)
        self._validate()

    def to_json(self) -> Dict:
        """get dictionary structure that can be stored as json with json.dumps()"""
        # dict creates copy preventing modifying original object
        json_dict = dict(self.__dict__)
        # overwrite traffic lights with json version
        json_dict["traffic_lights"] = [traffic_light.to_json() for traffic_light in self.traffic_lights]
        return json_dict

    @staticmethod
    def from_json(signalgroup_dict: Dict) -> SignalGroup:
        """Loading signal group from json (expected same json structure as generated with to_json)"""
        return SignalGroup(id=signalgroup_dict["id"],
                           min_greenyellow=signalgroup_dict["min_greenyellow"],
                           max_greenyellow=signalgroup_dict["max_greenyellow"],
                           min_red=signalgroup_dict["min_red"],
                           max_red=signalgroup_dict["max_red"],
                           min_nr=signalgroup_dict["min_nr"],
                           max_nr=signalgroup_dict["max_nr"],
                           traffic_lights=[TrafficLight.from_json(traffic_light_dict)
                                           for traffic_light_dict in signalgroup_dict["traffic_lights"]]
                           )

    def _validate(self) -> None:
        """
        validate the arguments provided to this object
        :return: - (raises ValueError if validation does not pass)
        """
        if not isinstance(self.traffic_lights, list):
            raise ValueError("traffic_lights should be a list of TrafficLight objects")
        for traffic_light in self.traffic_lights:
            if not isinstance(traffic_light, TrafficLight):
                raise ValueError("traffic_lights should be a list of TrafficLight objects")

        if not self.min_greenyellow >= 0:
            raise ValueError("min_greenyellow must be a non-negative number")
        if not 0 < self.max_greenyellow >= self.min_greenyellow:
            raise ValueError("max_greenyellow must be a positive number exceeding (or equal to) min_greenyellow")

        if not self.min_red >= 0:
            raise ValueError("min_red must be a non-negative number")
        if not 0 < self.max_red >= self.min_red:
            raise ValueError("max_red must be a positive number exceeding (or equal to) min_red")

        if not self.min_nr >= 1:
            raise ValueError("min_nr must be a positive integer")
        if not int(self.max_nr) >= int(self.min_nr):
            raise ValueError("max_nr must exceed or equal min_nr")


