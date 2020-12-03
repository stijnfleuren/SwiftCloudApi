from typing import Optional, Union, List

from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule
from swift_cloud_py.entities.intersection.sg_relations import SyncStart, Coordination, PreStart


def validate_other_sg_relations(intersection: Intersection, fts: FixedTimeSchedule, tolerance: float = 10**(-2)):
    """
    Ensure all sync starts, coordinations and prestarts are satisfied.
    :param intersection: intersection containing these inter signal group relations
    :param fts: fixed-time schedule to validate
    :param tolerance: tolerance in seconds for violating safety restrictions
    :raises ValueError if validations fail
    """
    for other_relation in intersection.other_relations:  # loop over all other-relations
        shift = get_other_sg_relation_shift(other_relation=other_relation, fts=fts, tolerance=tolerance)
        if shift is None:
            raise SafetyViolation(
                f"{other_relation.__class__} between '{other_relation.from_id}' and {other_relation.to_id}' are "
                f"not satisfied.")


def get_other_sg_relation_shift(other_relation: Union[Coordination, PreStart, SyncStart], fts: FixedTimeSchedule,
                                tolerance: float = 10**(-2)) -> Optional[int]:
    """
    Find a shift 'shift' of the greenyellow intervals such that the specified inter signal group relation is satisfied
     for each pair {(id_from, index), (id_to, index + shift)} of greenyellow intervals of signal groups id_from and
     id_to, where (id, index) refers to the greenyellow interval with index 'index' of signal group with id 'id'.
    :param other_relation: the inter signal group relation for which we want to find the shift.
    :param fts: fixed-time schedule.
    :param tolerance: tolerance in seconds for violating safety restrictions
    :return: the shift (None if no such shift can be found).
    """
    # Get the greenyellow intervals of the associated signal groups
    intervals_from = fts.get_greenyellow_intervals(signalgroup=other_relation.from_id)
    intervals_to = fts.get_greenyellow_intervals(signalgroup=other_relation.to_id)

    if len(intervals_from) != len(intervals_to):
        raise SafetyViolation(
            f"Signal groups {other_relation.__class__} should have the same number of GreenYellowPhases;"
            f"this is not satisfied for signalgroups {other_relation.from_id} and {other_relation.to_id}")

    # Matrix of size len(intervals_to) x len(intervals_from)
    matches = [[False] * len(intervals_to)] * len(intervals_from)

    # for each greenyellow interval of signal group with id 'other_relation.from_id' we try to find which of the
    #  greenyellow intervals of the signal group with id 'other_relation.to_id' satisfy the specified inter signal group
    #  relation w.r.t. this greenyellow interval
    for index_from, interval_from in enumerate(intervals_from):
        matches[index_from] = find_other_sg_relation_matches(other_relation=other_relation, fts=fts,
                                                             index_from=index_from, tolerance=tolerance)

    # does an unambiguous shift (reindexing) of the greenyellow intervals of signal group with id 'other_relation.to_id'
    #  exist
    return get_shift_of_one_to_one_match(matches=matches)


def get_shift_of_one_to_one_match(matches: List[List[bool]]) -> Optional[int]:
    """
    Matches is an n x n matrix representing a directed bipartite graph.
    Item i is connected to item j if matches[i][j] = True
    We try to find a shift k such that each item i is matched to an item j + shift

    usecase:
     for other_relations a shift 'shift' of the greenyellow intervals must exist such that other_relation is satisfied
     for each pair {(id_from, index), (id_to, index + shift)} of greenyellow intervals of signal groups id_from and
     id_to.
    :param matches: n x n matrix
    :return: shift or None if no such shift can be found
    :raises ValueError when matches is not an nxn boolean matrix
    """
    value_error_message = "matches should be an nxn boolean matrix"
    n = len(matches)
    if not isinstance(matches, list):
        raise ValueError(value_error_message)
    for row in matches:
        if not isinstance(matches, list) or len(row) != n:
            raise ValueError(value_error_message)
        if not all(isinstance(item, bool) for item in row):
            raise ValueError(value_error_message)

    for shift in range(n):
        # example:
        #  suppose matches equals:
        #      [[False, True, False], [False, False, True],[True, False, False]]
        #  then a shift of 1 to the left would give
        #      np.array([[True, False, False], [False, True, False],[False, False, True]])
        #  this has all diagonal elements
        #  below we do this check more efficiently for a shift of 'shift' to the left.
        if all(matches[row][(row + shift) % n] for row in range(n)):
            return shift
    return None


def find_other_sg_relation_matches(other_relation: Union[SyncStart, Coordination, PreStart], fts: FixedTimeSchedule,
                                   index_from: int, tolerance: float = 10**(-2)) -> List[bool]:
    """
    Find the greenyellow intervals of the signal group with id 'other_relation.to_id' that satisfies the specified
    inter signalgroup relation w.r.t. the greenyellow interval of signal group other_relation.from_id at index
    'index_from'
    :param other_relation: the other relation (sync start, coordination or prestart)
    :param fts: fixed-time schedule
    :param index_from: see above
    :param tolerance: tolerance in seconds for violating safety restrictions
    :return: boolean list indicating the matches.
    """
    # Get the greenyellow intervals of the associated signal groups
    interval_from = fts.get_greenyellow_interval(signalgroup=other_relation.from_id, k=index_from)
    intervals_to = fts.get_greenyellow_intervals(signalgroup=other_relation.to_id)

    matches = [False] * len(intervals_to)
    time_from = interval_from.start_greenyellow
    for index_to in range(len(intervals_to)):
        time_to = intervals_to[index_to].start_greenyellow

        # determine the desired range of the time between time_from and time_to.
        if isinstance(other_relation, SyncStart):
            min_time = 0
            max_time = 0
        elif isinstance(other_relation, Coordination):
            min_time = other_relation.coordination_time
            max_time = other_relation.coordination_time
        elif isinstance(other_relation, PreStart):
            min_time = other_relation.min_prestart
            max_time = other_relation.max_prestart
        else:
            raise NotImplementedError

        # Determine the actual time between time_from and time_to. We correct for min_time potentially being negative.
        time_between = (time_to - time_from - (min_time - tolerance)) % fts.period + (min_time - tolerance)

        # Note that result is time_between in [other_relation.min_time, other_relation.min_time + period]
        if min_time - tolerance < time_between < max_time + tolerance:
            matches[index_to] = True

    return matches
