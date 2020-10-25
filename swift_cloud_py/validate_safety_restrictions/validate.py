from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.validate_safety_restrictions.validate_bounds import validate_bounds
from swift_cloud_py.validate_safety_restrictions.validate_conflicts import validate_conflicts


def validate_safety_restrictions(intersection: Intersection, fixed_time_schedule: FixedTimeSchedule) -> None:
    """
    Check if the fixed-time schedule satisfies the safety restrictions such as bounds on greenyellow times
    and bounds on red times.
    intersection: intersection object (this object also contains safety restrictions that a
    fixed-time schedule should satisfy)

    This method raises a SafetyViolation-exception if the safety restrictions are not satisfied.
    """
    validate_bounds(intersection=intersection, fts=fixed_time_schedule)
    validate_conflicts(intersection=intersection, fts=fixed_time_schedule)
