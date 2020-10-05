import json
import logging
import os

from swift_cloud_py.enums import ObjectiveEnum
from swift_cloud_py.swift_cloud_api import SwiftMobilityCloudApi
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


def minimizing_period_duration(print_fixed_time_schedule: bool = False):
    """
    In this example (given a traffic scenario) we search for the fixed-time schedule with the smallest period duration
    for which none of the traffic lights are oversatured.

    NOTE:
    To run the example below you need credentials to invoke the swift mobility cloud api.
    To this end, you need to specify the following environment variables:
    - smc_api_key: the access key of your swift mobility cloud api account
    - smc_api_secret: the secret access key of your swift mobility cloud api account
    If you do not have such an account yet, please contact cloud_api@swiftmobility.eu.

    Tested with Swift Mobility Desktop 0.7.0.alpha
    """
    logging.info(f"Running example '{os.path.basename(__file__)}'")
    # absolute path to .json file that has been exported from swift mobility desktop
    root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir))
    smd_export = os.path.join(root_dir, "examples", "example_smd_export.json")

    # retrieve the json structure from the file
    with open(smd_export, "r") as f:
        json_dict = json.load(f)

    logging.info(f"Loading intersection and traffic situation from disk")
    intersection = Intersection.from_json(intersection_dict=json_dict["intersection"])
    arrival_rates = ArrivalRates.from_json(arrival_rates_dict=json_dict["arrival_rates"])
    logging.info(f"Loaded intersection and traffic situation from disk")

    logging.info(f"Minimizing period duration")
    fixed_time_schedule, phase_diagram, objective_value = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, min_period_duration=30, max_period_duration=180,
        objective=ObjectiveEnum.min_period)

    logging.info(f"Minimized period duration: {objective_value:.2f} seconds")

    if print_fixed_time_schedule:
        logging.info(fixed_time_schedule)
        logging.info(phase_diagram)


if __name__ == "__main__":
    minimizing_period_duration()
