from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.validate_safety_restrictions.validate_bounds import validate_bounds
from swift_cloud_py.validate_safety_restrictions.validate_completeness import validate_completeness
from swift_cloud_py.validate_safety_restrictions.validate_conflicts import validate_conflicts
from swift_cloud_py.validate_safety_restrictions.validate_other_sg_relations import validate_other_sg_relations


def validate_safety_restrictions(intersection: Intersection, fixed_time_schedule: FixedTimeSchedule,
                                 tolerance: float = 10**(-2)) -> None:
    """
    Check if the fixed-time schedule satisfies the safety restrictions such as bounds on greenyellow times
    and bounds on red times.
    :param intersection: intersection object (this object also contains safety restrictions that a
    fixed-time schedule should satisfy)
    :param fixed_time_schedule: the schedule that we would like to validate
    :param tolerance: tolerance in seconds for violating safety restrictions

    This method raises a SafetyViolation-exception if the safety restrictions are not satisfied.
    """
    validate_bounds(intersection=intersection, fts=fixed_time_schedule, tolerance=tolerance)
    validate_conflicts(intersection=intersection, fts=fixed_time_schedule, tolerance=tolerance)
    validate_other_sg_relations(intersection=intersection, fts=fixed_time_schedule, tolerance=tolerance)
    validate_completeness(intersection=intersection, fts=fixed_time_schedule)
