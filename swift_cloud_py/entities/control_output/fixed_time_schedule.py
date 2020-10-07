from __future__ import annotations  # allows using a class as typing inside the same class

from typing import Dict, List

from swift_cloud_py.entities.intersection.signalgroup import SignalGroup


def sort_by_name(name: str):
    """ function needed to sort signal groups by name """
    return len(name), name


class FixedTimeSchedule:
    """
    Periodically repeating schedule specifying when signal groups have a greenyellow interval.
    """
    def __init__(self, greenyellow_intervals: Dict[str, List[GreenYellowInterval]], period: float) -> None:
        self.greenyellow_intervals = greenyellow_intervals
        self.period = float(period)

    def get_greenyellow_intervals(self, signalgroup: SignalGroup) -> List[GreenYellowInterval]:
        """
        get all green intervals of signal group with id signalgroup.id
        :param signalgroup:
        :return:
        """
        return self.greenyellow_intervals[signalgroup.id]

    def get_greenyellow_interval(self, signalgroup: SignalGroup, k: int) -> GreenYellowInterval:
        """
        get the green intervals k (index starts at 0!) of signal group with id signalgroup.id
        :param signalgroup:
        :param k:
        :return:
        """
        return self.greenyellow_intervals[signalgroup.id][k]

    def to_json(self) -> Dict:
        """get dictionary structure that can be stored as json with json.dumps()"""
        return {"greenyellow_intervals": {sg_id: [greenyellow_interval.to_json()
                                                  for greenyellow_interval in greenyellow_intervals]
                                          for sg_id, greenyellow_intervals in self.greenyellow_intervals.items()},
                "period": self.period}

    @staticmethod
    def from_json(fts_dict: Dict) -> FixedTimeSchedule:
        """Loading fixed-time schedule from json (expected same json structure as generated with to_json)"""
        return FixedTimeSchedule(greenyellow_intervals={sg_id: [GreenYellowInterval.from_json(
            greenyellow_interval_list=greenyellow_interval_list)
            for greenyellow_interval_list in greenyellow_interval_lists]
            for sg_id, greenyellow_interval_lists in fts_dict["greenyellow_intervals"].items()},
            period=fts_dict["period"])

    def __str__(self) -> str:
        """string representation of object"""
        string = "fixed time schedule:\n"
        string += f"\tperiod: {self.period}\n"
        string += f"\tgreenyellow intervals:"
        max_name = max(len(sg_id) for sg_id in self.greenyellow_intervals)

        # sort by name
        greenyellow_interval_tuples = sorted(self.greenyellow_intervals.items(),
                                             key=lambda item: sort_by_name(item[0]))
        for sg_id, greenyellow_intervals in greenyellow_interval_tuples:
            string += "\n"
            # signal group name followed by semicolon, left aligned with width of max_name + 2
            string += f"\t\t{sg_id + ':':<{max_name + 2}}"
            for interval_index, interval in enumerate(greenyellow_intervals):
                if 0 < interval_index < len(greenyellow_intervals) - 1:
                    string += ", "
                elif 0 < interval_index == len(greenyellow_intervals) - 1:
                    string += " and "
                string += f"{str(interval)}"
        return string


class GreenYellowInterval:
    """
    A greenyellow interval; this is a general representation of the green interval itself and any other signal state
    (other than the pure red signal state) leading up to or following the green interval. For example,
    in the Netherlands the greenyellow interval would consist of the green interval followed by a yellow interval.
    In the UK, this greenyellow interval would consist of a yellow-red interval, followed by a green interval,
    succeeded by a yellow interval.
    """

    def __init__(self, start_greenyellow: float, end_greenyellow: float) -> None:
        # by converting to the correct data type we ensure correct types are used
        self.start_greenyellow = float(start_greenyellow)
        self.end_greenyellow = float(end_greenyellow)
        assert start_greenyellow >= 0, "strart_greenyellow should be non-negative"
        assert end_greenyellow >= 0, "end_greenyellow should be non-negative"

    def to_json(self) -> List:
        """get json serializable structure that can be stored as json with json.dumps()"""
        return [self.start_greenyellow, self.end_greenyellow]

    @staticmethod
    def from_json(greenyellow_interval_list: List) -> GreenYellowInterval:
        """Loading greenyellow interval from json (expected same json structure as generated with to_json)"""
        return GreenYellowInterval(*greenyellow_interval_list)

    def __str__(self) -> str:
        """string representation of object"""
        return f"[{self.start_greenyellow:.2f}, {self.end_greenyellow:.2f}]"
