import json
import logging
import os

from swift_cloud_py.enums import ObjectiveEnum
from swift_cloud_py.swift_cloud_api import SwiftMobilityCloudApi
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


def optimize_multiple_schedules():
    """
    Example showing how to:
    - retrieve intersection information and arrival rates from a json file exported from Swift Mobility Desktop.
    - use this information to optimize fixed-time schedules

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

    logging.info(f"Minimizing average experienced delay")
    best_fixed_time_schedule, best_phase_diagram, objective_value, warm_start_info = \
        SwiftMobilityCloudApi.get_optimized_fts(
            intersection=intersection, arrival_rates=arrival_rates, min_period_duration=30, max_period_duration=180,
            objective=ObjectiveEnum.min_delay)

    logging.info(f"Average experienced delay: {objective_value:.2f} seconds")
    logging.info(best_fixed_time_schedule)
    logging.info(best_phase_diagram)

    logging.info(f"Finding second best schedule")
    second_best_fixed_time_schedule, second_best_phase_diagram, objective_value, warm_start_info = \
        SwiftMobilityCloudApi.get_optimized_fts(
            intersection=intersection, arrival_rates=arrival_rates, min_period_duration=30, max_period_duration=180,
            objective=ObjectiveEnum.min_delay, fixed_time_schedules_to_exclude=[best_fixed_time_schedule],
            warm_start_info=warm_start_info)

    logging.info(f"Average experienced delay of second best schedule: {objective_value:.2f} seconds")
    logging.info(second_best_fixed_time_schedule)
    logging.info(second_best_phase_diagram)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    optimize_multiple_schedules()
