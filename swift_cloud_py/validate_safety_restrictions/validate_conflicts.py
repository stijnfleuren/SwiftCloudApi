from typing import Tuple, List

from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.control_output.fixed_time_schedule import GreenYellowInterval, FixedTimeSchedule
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.sg_relations import Conflict


def validate_conflicts(intersection: Intersection, fts: FixedTimeSchedule):
    """
    Ensure all conflicts are satisfied.
    :param intersection: intersection object (this object contains all conflicts and associated minimum clearance times
    that should be satisfied)
    :param fts: fixed-time schedule to check
    :raises SafetyViolation if validations fail
    """

    for conflict in intersection.conflicts:
        intervals1 = fts.get_greenyellow_intervals(signalgroup=conflict.id1)
        intervals2 = fts.get_greenyellow_intervals(signalgroup=conflict.id2)
        for index1, interval1 in enumerate(intervals1):
            for index2, interval2 in enumerate(intervals2):
                if not conflict_satisfied(interval1=interval1, interval2=interval2, period=fts.period,
                                          conflict=conflict):
                    raise SafetyViolation(
                        f"Conflict not satified for interval {index1:d} of '{conflict.id1:s}' "
                        f"and interval {index2:d} of '{conflict.id2:s}'.")


def overlap_of_intervals(interval1: Tuple[float, float], interval2: Tuple[float, float], period: float
                         ) -> List[Tuple[float, float]]:
    """ compute the overlap of two periodic intervals.
    Intervals have format (starting_time, ending_time), where starting_time and ending_time are between zero and
    the period duration. Output is a list of intervals (as the intersection could potentially be two
    disjunct intervals"""

    # both are green at time T
    if interval1[0] > interval1[1] and interval2[0] > interval2[1]:
        return [(max(interval1[0], interval2[0]), min(interval1[1], interval2[1]))]

    # only one of the two intervals could potentially still include time=period
    # if interval1 includes time=period, then swap the intervals so that interval 2 includes this period
    if interval1[0] > interval1[1]:
        interval1, interval2 = interval2, interval1

    # convert the second interval to two intervals if it includes time=period; let [s,e] be interval2, then we use the
    # two intervals [s-period, e], [s,e+period], which because of periodicity are equivalent
    if interval2[0] < interval2[1]:  # if this interval does not include time=period
        interval_list2_non_periodic = [interval2]
    else:
        interval_list2_non_periodic = [(interval2[0] - period, interval2[1]),
                                       (interval2[0], interval2[1] + period)]

    # compute the intersection of interval1 with the interval(s) in interval_list2_non_periodic
    overlapping_intervals = []
    for interval2_non_periodic in interval_list2_non_periodic:
        max_start = max(interval1[0], interval2_non_periodic[0])
        min_end = min(interval1[1], interval2_non_periodic[1])
        # if the two intervals overlap
        if max_start < min_end:
            # we store the interval (but first convert ot back to the range [0, period))
            overlapping_intervals.append(
                (max_start % period, min_end % period))
    return overlapping_intervals


def conflict_satisfied(interval1: GreenYellowInterval, interval2: GreenYellowInterval, period: float,
                       conflict: Conflict):
    forbidden_interval_for_sg2 = ((interval1.start_greenyellow - conflict.setup21 + 10**(-3)) % period,
                                  (interval1.end_greenyellow + conflict.setup12 - 10**(-3)) % period)
    intersection = overlap_of_intervals(interval1=forbidden_interval_for_sg2,
                                        interval2=(interval2.start_greenyellow, interval2.end_greenyellow),
                                        period=period)
    if intersection:
        return False
    else:
        return True
