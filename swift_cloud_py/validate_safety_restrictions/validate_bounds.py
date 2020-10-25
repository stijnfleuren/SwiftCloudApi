from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule
from swift_cloud_py.entities.intersection.intersection import Intersection

EPSILON = 10**(-3)  # small value used in checks to allow a very small violation of constraints caused by numeric errors


def validate_bounds(intersection: Intersection, fts: FixedTimeSchedule):
    """
    Ensure that all bounds on greenyellow and red times are satiesfied for the specified fixed-time schedule.
    :param intersection: intersection object (this object also contains safety restrictions that a
    fixed-time schedule should satisfy)
    :param fts: FixedTimeSchedule object for which we want to check the safety restrictions
    :raises ValueError if validations fail
    """
    # check the duration of greenyellow times and red times
    for signalgroup in intersection.signalgroups:
        greenyellow_intervals = fts.get_greenyellow_intervals(signalgroup=signalgroup)
        # end of the last greenyellow interval
        prev_red_switch = greenyellow_intervals[-1].end_greenyellow

        # loop over the greenyellow intervals
        for _, interval in enumerate(greenyellow_intervals):
            # the duration of the red interval preceeding this greenyellow interval
            red_time = (interval.start_greenyellow - prev_red_switch + EPSILON) % fts.period - EPSILON

            # the duration of the greenyellow interval
            greenyellow_time = (interval.end_greenyellow - interval.start_greenyellow + EPSILON) % fts.period - EPSILON

            # check these durations for violations of the minimum and maximum durations
            if red_time < signalgroup.min_red - EPSILON:
                raise SafetyViolation(
                    f"Red time of sg '{signalgroup.id}' too short ({red_time:3.1f} seconds while "
                    f"min={signalgroup.min_red:3.1f})")

            if red_time > signalgroup.max_red + EPSILON:
                raise SafetyViolation(
                    f"Red time of sg '{signalgroup.id}' too long ({red_time:3.1f} seconds "
                    f"while max={signalgroup.max_red:3.1f})")
            if greenyellow_time < signalgroup.min_greenyellow - EPSILON:
                raise SafetyViolation(
                    f"Greenyellow time of sg '{signalgroup.id}' too short ({greenyellow_time:3.1f} seconds while "
                    f"min={signalgroup.min_greenyellow:3.1f})")
            if greenyellow_time > signalgroup.max_greenyellow + EPSILON:
                raise SafetyViolation(
                    f"Greenyellow time of sg '{signalgroup.id}' too large ({greenyellow_time:3.1f} seconds while "
                    f"max={signalgroup.max_greenyellow:3.1f})")
            prev_red_switch = interval.end_greenyellow
