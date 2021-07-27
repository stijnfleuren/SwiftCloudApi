from swift_cloud_py.common.errors import SafetyViolation
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.periodic_order import PeriodicOrder

EPSILON = 10**(-6)  # small value used in checks to correct for numeric inaccuracies


def validate_fixed_orders(intersection: Intersection, fts: FixedTimeSchedule):
    for periodic_order in intersection.periodic_orders:
        validate_fixed_order(intersection=intersection, fts=fts, periodic_order=periodic_order)


def validate_fixed_order(intersection: Intersection, fts: FixedTimeSchedule, periodic_order: PeriodicOrder):
    first_signalgroup = intersection.get_signalgroup(signalgroup_id=periodic_order.order[0])
    first_interval_start = fts.get_greenyellow_interval(first_signalgroup, k=0).start_greenyellow
    prev_switch = 0
    for signalgroup in periodic_order.order:
        for interval in fts.get_greenyellow_intervals(signalgroup):
            # shift schedule such that first greenyellow interval of the first signalgroup in the order starts at time=0
            switch = (interval.start_greenyellow - first_interval_start + EPSILON) % fts.period - EPSILON
            if switch < prev_switch:
                raise SafetyViolation(f"Periodic order {periodic_order.to_json()} is violated")
            prev_switch = switch
