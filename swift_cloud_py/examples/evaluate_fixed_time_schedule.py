import json
import logging
import os

from swift_cloud_py.enums import ObjectiveEnum
from swift_cloud_py.swift_cloud_api import SwiftMobilityCloudApi
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


def evaluate_fixed_time_schedule(print_fixed_time_schedule: bool = False):
    """
    In this example we show how to evaluate a fixed-time schedule.

    Use case: comparing two fixed-time schedules (perhaps not optimized via this api) on expected performance.

    NOTE:
    To run the example below you need credentials to invoke the swift mobility cloud api.
    To this end, you need to specify the following environment variables:
    - smc_api_key: the access key of your swift mobility cloud api account
    - smc_api_secret: the secret access key of your swift mobility cloud api account
    If you do not have such an account yet, please contact cloud_api@swiftmobility.eu.

    In this example, we load an intersection from disk (export of Swift Mobility Desktop). You can download this
    file (example_smd_export.json) from
    https://github.com/stijnfleuren/SwiftCloudApi/tree/master/swift_cloud_py/examples
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
    fixed_time_schedule, phase_diagram, objective_value, _ = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, min_period_duration=30, max_period_duration=180,
        objective=ObjectiveEnum.min_delay, horizon=2)

    logging.info(f"Average experienced delay: {objective_value:.2f} seconds")

    if print_fixed_time_schedule:
        logging.info(fixed_time_schedule)
        logging.info(phase_diagram)

    # this should return the same estimated delay. With this functionality we could evaluate the expected performance
    #  of any fixed-time schedule.
    logging.info(f"Evaluate this schedule")
    kpis = SwiftMobilityCloudApi.evaluate_fts(intersection=intersection, fixed_time_schedule=fixed_time_schedule,
                                              arrival_rates=arrival_rates, horizon=2)
    logging.info(f"Output: {kpis}")
