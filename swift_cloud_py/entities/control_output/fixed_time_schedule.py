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

        self._validate()

    def get_greenyellow_intervals(self, signalgroup: SignalGroup) -> List[GreenYellowInterval]:
        """
        get all green intervals of signal group with id signalgroup.id
        :param signalgroup:
        :return:
        """
        if signalgroup.id not in self.greenyellow_intervals:
            raise ValueError("Unkown signalgroup")
        return self.greenyellow_intervals[signalgroup.id]

    def get_greenyellow_interval(self, signalgroup: SignalGroup, k: int) -> GreenYellowInterval:
        """
        get the green intervals k (index starts at 0!) of signal group with id signalgroup.id
        :param signalgroup:
        :param k:
        :return:
        """
        if signalgroup.id not in self.greenyellow_intervals:
            raise ValueError("Unkown signalgroup")
        if k >= len(self.greenyellow_intervals[signalgroup.id]):
            raise ValueError("Trying to access greenyellow interval at index {k}, "
                             "but only indexes 0 until {len(self.greenyellow_intervals[signalgroup.id]) - 1} exist")

        return self.greenyellow_intervals[signalgroup.id][k]

    def _validate(self) -> None:
        """ Validate input arguments of FixedTimeSchedule; raises ValueError if validation does not pass"""
        self._validate_types()

        for _id, intervals in self.greenyellow_intervals.items():
            self._validate_not_overlapping_and_sorted(intervals=intervals)
            for interval in intervals:
                self._validate_interval_within_period(interval=interval)

    def _validate_types(self):
        """validate the types of the input arguments"""
        # validate structure of greenyellow_intervals
        error_message = "greenyellow_intervals should be a dictionary mapping from a signal group id (str) to " \
                        "a list of GreenYellowIntervals (List[float])"
        if not isinstance(self.greenyellow_intervals, dict):
            raise ValueError(error_message)
        for _id, intervals in self.greenyellow_intervals.items():

            if not isinstance(_id, str):
                raise ValueError(error_message)
            if not isinstance(intervals, list):
                raise ValueError(error_message)
            for interval in intervals:
                if not isinstance(interval, GreenYellowInterval):
                    raise ValueError(error_message)

    def _validate_interval_within_period(self, interval: GreenYellowInterval):
        """ validate a single greenyellow interval"""
        if interval.start_greenyellow > self.period:
            raise ValueError("start_greenyellow may not exceed period duration")
        if interval.end_greenyellow > self.period:
            raise ValueError("end_greenyellow may not exceed period duration")

    def _validate_not_overlapping_and_sorted(self, intervals: List[GreenYellowInterval]):
        """validate if the greenyellowintervals of one signal group are not overlapping or not in the correct order"""
        first_interval = min(intervals, key=lambda interval: interval.start_greenyellow)
        index_first_interval = intervals.index(first_interval)
        # ensure that the greenyellow interval that starts first is also first
        intervals_sorted = intervals[index_first_interval:] + intervals[:index_first_interval]

        # test correct order
        prev_start_greenyellow = intervals_sorted[0].start_greenyellow
        for interval in intervals_sorted[1:]:
            if interval.start_greenyellow <= prev_start_greenyellow:
                raise ValueError(
                    "The greenyellow intervals of a signal group must be provided in the correct (periodic)"
                    "order, e.g., [[10, 40], [50, 80], [80, 100]] and not [[10, 40], [80, 100], [50, 80]]")
            prev_start_greenyellow = interval.start_greenyellow

        # test non-overlapping
        prev_time = 0
        for k, interval in enumerate(intervals_sorted):
            if interval.start_greenyellow < prev_time:
                raise ValueError("The greenyellow intervals of a signal group must be non-overlapping")
            prev_time = interval.start_greenyellow

            if (k < len(intervals_sorted) - 1 or interval.end_greenyellow >= intervals_sorted[0].start_greenyellow) \
                    and interval.end_greenyellow < prev_time:
                print("end failed", interval)
                raise ValueError("The greenyellow intervals of a signal group must be non-overlapping")

            prev_time = interval.end_greenyellow

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

    def __eq__(self, other: FixedTimeSchedule):
        if not isinstance(other, FixedTimeSchedule):
            raise ValueError("can only compare a FixedTimeSchedule to a FixedTimeSchedule")

        # comparing the period duration
        if self.period != other.period:
            return False

        # comparing the ids
        ids = {_id for _id in self.greenyellow_intervals}
        other_ids = {_id for _id in other.greenyellow_intervals}
        if ids != other_ids:
            return False

        # comparing the greenyellow intervals
        for _id in ids:
            if self.greenyellow_intervals[_id] != other.greenyellow_intervals[_id]:
                return False

        return True


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

    def __eq__(self, greenyellow_interval: GreenYellowInterval):
        if not isinstance(greenyellow_interval, GreenYellowInterval):
            raise ValueError("can only compare a GreenYellowInterval to a GreenYellowInterval")
        if greenyellow_interval.start_greenyellow == self.start_greenyellow and \
                greenyellow_interval.end_greenyellow == self.end_greenyellow:
            return True
        else:
            return False

    def __str__(self) -> str:
        """string representation of object"""
        return f"[{self.start_greenyellow:.2f}, {self.end_greenyellow:.2f}]"
