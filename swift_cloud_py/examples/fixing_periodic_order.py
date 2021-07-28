import logging
import os

from swift_cloud_py.entities.intersection.periodic_order import PeriodicOrder
from swift_cloud_py.enums import ObjectiveEnum
from swift_cloud_py.swift_cloud_api import SwiftMobilityCloudApi
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.intersection.sg_relations import Conflict
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


def fix_order_and_optimize():
    """
    This example shows how to ask for a fixed-time schedule that adheres to a specified fix order in which
    the signalgroups should receive their greenyellow interval.
    """
    logging.info(f"Running example '{os.path.basename(__file__)}'")
    # signal group consisting of two traffic light allowing 1 or 2 greenyellow intervals per repeating period.
    traffic_light1 = TrafficLight(capacity=1800, lost_time=2.2)
    traffic_light2 = TrafficLight(capacity=1810, lost_time=2.1)
    signalgroup1 = SignalGroup(id="2", traffic_lights=[traffic_light1, traffic_light2], min_greenyellow=10,
                               max_greenyellow=100, min_red=10, max_red=100, min_nr=1, max_nr=2)

    # signal group consisting of one traffic light allowing 1 greenyellow interval (default) per repeating period.
    traffic_light3 = TrafficLight(capacity=1650, lost_time=3.0)
    signalgroup2 = SignalGroup(id="5", traffic_lights=[traffic_light3], min_greenyellow=10,
                               max_greenyellow=100, min_red=10, max_red=100)

    # signal group consisting of one traffic light allowing 1 greenyellow interval (default) per repeating period.
    traffic_light4 = TrafficLight(capacity=1800, lost_time=2.1)
    signalgroup3 = SignalGroup(id="8", traffic_lights=[traffic_light4], min_greenyellow=10,
                               max_greenyellow=100, min_red=10, max_red=100)

    # conflicts & clearance times
    conflict12 = Conflict(id1=signalgroup1.id, id2=signalgroup2.id, setup12=1, setup21=2)
    conflict13 = Conflict(id1=signalgroup1.id, id2=signalgroup3.id, setup12=2, setup21=1)
    conflict23 = Conflict(id1=signalgroup2.id, id2=signalgroup3.id, setup12=2, setup21=3)

    # initialize intersection object
    intersection = Intersection(signalgroups=[signalgroup1, signalgroup2, signalgroup3],
                                conflicts=[conflict12, conflict13, conflict23])

    # set associated arrival rates
    arrival_rates = ArrivalRates(id_to_arrival_rates={"2": [800, 700], "5": [150], "8": [180]})
    logging.info(f"Not yet requesting any fixed order of greenyellow intervals")
    logging.info(f"Minimizing average experienced delay")
    # optimize fixed-time schedule
    fixed_time_schedule, phase_diagram, objective_value, _ = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, objective=ObjectiveEnum.min_delay)

    logging.info(f"Average experienced delay {objective_value: .3f} seconds")
    logging.info(fixed_time_schedule)
    logging.info(phase_diagram)

    logging.info(f"Requesting order: 2 -> 8 -> 5 -> ")
    # initialize intersection object
    intersection = Intersection(signalgroups=[signalgroup1, signalgroup2, signalgroup3],
                                conflicts=[conflict12, conflict13, conflict23],
                                periodic_orders=[PeriodicOrder(order=["2", "8", "5"])])
    logging.info(f"Minimizing average experienced delay")
    # optimize fixed-time schedule
    fixed_time_schedule, phase_diagram, objective_value, _ = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, objective=ObjectiveEnum.min_delay)

    logging.info(f"Average experienced delay {objective_value: .3f} seconds")
    logging.info(fixed_time_schedule)
    logging.info(phase_diagram)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    fix_order_and_optimize()
