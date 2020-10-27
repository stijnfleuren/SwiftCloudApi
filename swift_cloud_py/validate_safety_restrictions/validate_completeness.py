"""
Validate that all of the signal groups are included
"""
from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule
from swift_cloud_py.entities.intersection.intersection import Intersection


def validate_completeness(intersection: Intersection, fts: FixedTimeSchedule):
    """
    Ensures that greenyellow intervals are specified for all signalgroups
    :param intersection: intersection object containing the signal groups for which the greenyellow intervals should
    be specified
    :param fts: fixed-time schedule to validate
    :raises SafetyViolation if validations fail
    """
    for signalgroup in intersection.signalgroups:
        if not fts.includes_signalgroup(signalgroup=signalgroup):
            raise SafetyViolation(f"No greenyellow intervals specified for {signalgroup.id}")
        # if the signal group is included in the schedule, then check if the number of greenyellow intervals is >= 1
        if len(fts.get_greenyellow_intervals(signalgroup=signalgroup)) == 0:
            raise SafetyViolation(f"No greenyellow intervals specified for {signalgroup.id}")
