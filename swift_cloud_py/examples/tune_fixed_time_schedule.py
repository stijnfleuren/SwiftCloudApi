import json
import logging
import os

from swift_cloud_py.enums import ObjectiveEnum
from swift_cloud_py.swift_cloud_api import SwiftMobilityCloudApi
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


def tune_fixed_time_schedule(print_fixed_time_schedule: bool = False):
    """
    In this example we show how to tune a fixed-time schedule.

    Use case: Traffic situations change throughout the day. This function allows you to quickly adapt the green times
    of an existing fixed-time schedule to a new traffic situations. This can be used, for example, to adapt the
    maximum greenyellow times of a smart traffic light controller to the current traffic situation in real-time.

    NOTE:
    To run the example below you need credentials to invoke the swift mobility cloud api.
    To this end, you need to specify the following environment variables:
    - smc_api_key: the access key of your swift mobility cloud api account
    - smc_api_secret: the secret access key of your swift mobility cloud api account
    If you do not have such an account yet, please contact cloud_api@swiftmobility.eu.

    In this example, we load an intersection from disk (export of Swift Mobility Desktop). This functionality is tested
    with Swift Mobility Desktop 0.7.0.alpha.
    """
    logging.info(f"Running example '{os.path.basename(__file__)}'")
    # absolute path to .json file that has been exported from swift mobility desktop
    smd_export = os.path.join(os.path.join(os.path.abspath(__file__), os.pardir), "example_smd_export.json")

    # retrieve the json structure from the file
    with open(smd_export, "r") as f:
        json_dict = json.load(f)

    logging.info(f"Loading intersection and traffic situation from disk")
    intersection = Intersection.from_json(intersection_dict=json_dict["intersection"])
    arrival_rates = ArrivalRates.from_json(arrival_rates_dict=json_dict["arrival_rates"])
    logging.info(f"Loaded intersection and traffic situation from disk")

    logging.info(f"Minimizing delay")
    fixed_time_schedule, phase_diagram, objective_value = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, min_period_duration=30, max_period_duration=180,
        objective=ObjectiveEnum.min_delay, horizon=2)

    logging.info(f"Average experienced delay: {objective_value:.2f} seconds")

    if print_fixed_time_schedule:
        logging.info(fixed_time_schedule)
        logging.info(phase_diagram)

    # the more the traffic situation changes, the more effect tuning the fixed-time schedule has. In this example,
    # we only scale the amount of traffic.
    for scaling_factor in [0.95, 0.9, 0.7, 0.4]:
        logging.info(f"Evaluating schedule for situation with {(1-scaling_factor)*100 :.1f}% less traffic")

        arrival_rates_scaled = arrival_rates * scaling_factor

        kpis = SwiftMobilityCloudApi.evaluate_fts(intersection=intersection, fixed_time_schedule=fixed_time_schedule,
                                                  arrival_rates=arrival_rates_scaled, horizon=2)

        logging.info(f"Average experienced delay without tuning: {kpis.delay:.2f} seconds")

        logging.info(f"Tuning schedule for situation with {(1-scaling_factor)*100 :.1f}% less traffic")

        tuned_fixed_time_schedule, objective_value = SwiftMobilityCloudApi.get_tuned_fts(
            intersection=intersection, fixed_time_schedule=fixed_time_schedule, arrival_rates=arrival_rates_scaled,
            min_period_duration=30, max_period_duration=180, objective=ObjectiveEnum.min_delay, horizon=2)

        logging.info(f"Average experienced delay after tuning: {objective_value:.2f} seconds")

        if print_fixed_time_schedule:
            logging.info(fixed_time_schedule)
            logging.info(phase_diagram)
