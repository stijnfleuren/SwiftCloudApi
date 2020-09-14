import json
import os

from swift_cloud_py.enums import ObjectiveEnum
from swift_cloud_py.swift_cloud_api import SwiftMobilityCloudApi
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


def load_from_smd_and_run():
    """
    Example showing how to:
    - retrieve intersection information and arrival rates from a json file exported from Swift Mobility Export.
    - use this information to optimize fixed-time schedules
    
    Note important:
    To run the example below you need credentials to invoke the swift mobility cloud api.
    To this end, you need to specify the following environment variables:
    - smc_api_key: the access key of your swift mobility cloud api account
    - smc_api_secret: the secret access key of your swift mobility cloud api account
    If you do not have such an account yet, please contact cloud_api@swiftmobility.eu.
    
    Tested with Swift Mobility Desktop 0.7.0.alpha
    """
    # absolute path to .json file that has been exported from swift mobility desktop
    root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir))
    smd_export = os.path.join(root_dir, "examples", "example_smd_export.json")

    # retrieve the json structure from the file
    with open(smd_export, "r") as f:
        json_dict = json.load(f)

    intersection = Intersection.from_json(intersection_dict=json_dict["intersection"])
    arrival_rates = ArrivalRates.from_json(arrival_rates_dict=json_dict["arrival_rates"])

    # we are optimizing for a large intersection; it could take a while before it is finished
    fixed_time_schedule, phase_diagram, objective_value = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, objective=ObjectiveEnum.max_capacity)

    print("maximum sustainable increase (scaling factor) in traffic", objective_value)
    print(fixed_time_schedule)
    print(phase_diagram)

    # the following code indicates how to compute a phase diagram from a fixed-time schedule (note that now it makes
    #  no sense to do so as it was already computed above)
    phase_diagram = SwiftMobilityCloudApi.get_phase_diagram(intersection=intersection,
                                                            fixed_time_schedule=fixed_time_schedule)
    print(phase_diagram)


if __name__ == "__main__":
    load_from_smd_and_run()