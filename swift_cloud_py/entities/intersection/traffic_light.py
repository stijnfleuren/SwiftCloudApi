from __future__ import annotations  # allows using TrafficLight-typing inside TrafficLight-class

from copy import deepcopy
from typing import Optional, Dict


class TrafficLight:
    def __init__(self, capacity: float, lost_time: float, weight: Optional[float] = 1.0,
                 max_saturation: Optional[float] = None) -> None:
        """
        Traffic light object for which we want to plan greenyellow intervals. A greenyellow interval is a generic
         representation of the green interval itself and any other signal state (other than the pure red signal state)
         leading up to or following the green interval. For example, in the Netherlands the greenyellow interval would
         consist of the green interval followed by a yellow interval. In the UK, this greenyellow interval would consist
         of a yellow-red interval, followed by a green interval, succeeded by a yellow interval.
        :param capacity: capacity in PCE/h (personal car equivalent per hour)
        :param lost_time: time (in seconds) that is 'lost' every greenyellow interval due to accelerations (at start)
        and people stopping before the end of the yellow interval (if yellow follows green); the amount of PCE that
        is expected to depart during a greenyellow interval of gy seconds is (gy - lost_time) * capacity
        :param weight: importance of this traffic light (larger means more important); only relevant when
        minimizing the expected waiting time (delay) at the traffic lights; the delay at a traffic light with weight=2.0
        counts twice as hard as a delay at a traffic light with weight=1.0.
        :param max_saturation: maximum allowed saturation (1.0 is at the verge of oversaturation).
        """
        if max_saturation:
            assert max_saturation >= 0.0
        assert weight >= 0.0
        assert capacity >= 0.0
        assert lost_time >= 0.0
        # by converting to the correct data type we ensure correct types are used
        self.capacity = float(capacity)  # store capacity in PCE/second (instead of PCE/h)
        self.max_saturation = float(max_saturation) if max_saturation else None
        self.lost_time = float(lost_time)
        self.weight = float(weight)

    def to_json(self) -> Dict:
        """get dictionary structure that can be stored as json with json.dumps()"""
        # dict creates copy preventing modifying original object
        return dict(self.__dict__)

    @staticmethod
    def from_json(traffic_light_dict: Dict) -> TrafficLight:
        """Loading traffic light from json (expected same json structure as generated with to_json)"""
        return TrafficLight(capacity=traffic_light_dict["capacity"],
                            lost_time=traffic_light_dict["lost_time"],
                            weight=traffic_light_dict["weight"],
                            max_saturation=traffic_light_dict["max_saturation"])
