import json
import logging
import os

from swift_cloud_py.enums import ObjectiveEnum
from swift_cloud_py.swift_cloud_api import SwiftMobilityCloudApi
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.intersection.traffic_light import TrafficLight
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup
from swift_cloud_py.entities.intersection.sg_relations import Conflict, SyncStart, PreStart, Coordination
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


def create_intersection_and_optimize():
    """
    Example showing how to:
    - create traffic lights, signalgroups and intersections, ...
    - optimize a fixed-time schedule for this intersection

    Note important:
    To run the example below you need credentials to invoke the swift mobility cloud api.
    To this end, you need to specify the following environment variables:
    - smc_api_key: the access key of your swift mobility cloud api account
    - smc_api_secret: the secret access key of your swift mobility cloud api account
    If you do not have such an account yet, please contact cloud_api@swiftmobility.eu.
    """
    # signalgroup consisting of two traffic light allowing 1 or 2 greenyellow intervals per repeating period.
    traffic_light1 = TrafficLight(capacity=1800, lost_time=2.2)
    traffic_light2 = TrafficLight(capacity=1810, lost_time=2.1)
    signalgroup1 = SignalGroup(id="2", traffic_lights=[traffic_light1, traffic_light2], min_greenyellow=10,
                               max_greenyellow=100, min_red=10, max_red=100, min_nr=1, max_nr=2)

    # signalgroup consisting of one traffic light allowing 1 greenyellow interval (default) per repeating period.
    traffic_light3 = TrafficLight(capacity=1650, lost_time=3.0)
    signalgroup2 = SignalGroup(id="5", traffic_lights=[traffic_light3], min_greenyellow=10,
                               max_greenyellow=100, min_red=10, max_red=100)

    # signalgroup consisting of one traffic light allowing 1 greenyellow interval (default) per repeating period.
    traffic_light4 = TrafficLight(capacity=1800, lost_time=2.1)
    signalgroup3 = SignalGroup(id="8", traffic_lights=[traffic_light4], min_greenyellow=10,
                               max_greenyellow=100, min_red=10, max_red=100)

    # conflicts & clearance times
    conflict12 = Conflict(id1=signalgroup1.id, id2=signalgroup2.id, setup12=1, setup21=2)
    conflict13 = Conflict(id1=signalgroup1.id, id2=signalgroup3.id, setup12=1, setup21=2)
    conflict23 = Conflict(id1=signalgroup2.id, id2=signalgroup3.id, setup12=2, setup21=3)

    # initialize intersection object
    intersection = Intersection(signalgroups=[signalgroup1, signalgroup2, signalgroup3],
                                conflicts=[conflict12, conflict13, conflict23])

    # set associated arrival rates
    arrival_rates = ArrivalRates(id_to_arrival_rates={"2": [800, 700], "5": [150], "8": [180]})

    # optimize fixed-time schedule
    fixed_time_schedule, phase_diagram, objective_value = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, objective=ObjectiveEnum.min_delay)

    logging.info("Average experienced delay", objective_value)
    logging.info(fixed_time_schedule)
    logging.info(phase_diagram)

    # the following code indicates how to compute a phase diagram from a fixed-time schedule (note that now it makes
    #  no sense to do so as it was already computed above)
    phase_diagram = SwiftMobilityCloudApi.get_phase_diagram(intersection=intersection,
                                                            fixed_time_schedule=fixed_time_schedule)
    logging.info(phase_diagram)


if __name__ == "__main__":
    create_intersection_and_optimize()