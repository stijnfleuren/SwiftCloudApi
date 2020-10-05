import json
import logging
import os

from swift_cloud_py.enums import ObjectiveEnum
from swift_cloud_py.swift_cloud_api import SwiftMobilityCloudApi
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates


def maximize_intersection_capacity(print_fixed_time_schedule: bool = False):
    """
    In this example (given a traffic scenario) we search for the fixed-time schedule that maximizes the largest
    increase in traffic (scaling factor) that the intersection is able handle without becoming unstable/oversaturated.

    This is very useful information as it gives an indication as to how close the intersection is to being
    oversaturated.
     - An objective value of f < 1 indicates that the intersection is oversaturated for all (!) possible
       fixed-time schedules. For example, if f=0.8 then it is impossible to prevent oversaturation (with any
       traffic light controller!) unless the amount of traffic at the intersection decreases by at least 20%
       (=(1-0.8)*100)).
     - An objective value of > 1 indicates that it is possible to prevent oversaturation at this intersection.
       For example, if f=1.2, then the amount of traffic arriving at the intersection may still increase by 20% without
       the intersection becoming oversaturated (under optimal traffic light control!)

    Usecase 1: Monitoring
    We can in real-time monitor the traffic situation and quantify the amount of traffic arriving at the intersection.
    This information can again be used for traffic management (e.g., redirect traffic to relieve highly congested parts
    of the network).

    Usecase 2: Smart traffic-light control
    Low-traffic and high-traffic situations require a different control strategy. We can periodically evaluate the
    traffic situation in an automated manner (e.g., every 30 minutes). Based on the result (the value of f) we can
    (automatically!) select the control strategy that best matches the current traffic situation;
    this would be truly smart traffic-light control!

    Usecase 3: Quantitative support to decide which traffic-light control to update.
    Suppose traffic flow is not as smooth as desired at an intersection (e.g., queue lengths are large) while we can
    quantify the intersection to have sufficient capacity (e.g., f < 0.8). It, might be sensible to reevaluate the
    currently used traffic-light controller (and potentially update this controller). In this way, we can decide
    which traffic-light controllers need to be updated and focus effort on these controllers.

    On the other hand, if the capacity of the intersection is expected to be insufficient as well (e.g., f > 1.0), then
    this might motivate infrastructural changes (see next usecase).

    Usecase 4: Support for strategic decision making on infrastructural changes to the road network.
    Traffic situations may change overtime (e.g., due to urban development). Therefore, it is very important to
    periodically evaluate if any infrastructural changes (or policy changes by the government) are needed.

    This is a very difficult decision to be made with high impact; quantitative support is really useful when making
    these decisions. It is now possible, to evaluate the maximum traffic increase that the intersection/infrastructure
    is able to handle under optimal traffic light control. This could be used to answer questions like: is the
    capacity of our infrastructure (intersection) expected to still be sufficient in 3 years?

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

    logging.info(f"Maximizing capacity of the intersection")
    fixed_time_schedule, phase_diagram, objective_value = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, min_period_duration=30, max_period_duration=180,
        objective=ObjectiveEnum.max_capacity)

    logging.info(f"Maximum sustainable increase in traffic {(objective_value - 1) * 100:.2f}%")

    if print_fixed_time_schedule:
        logging.info(fixed_time_schedule)
        logging.info(phase_diagram)

    scaling_factor = 1.2
    logging.info(f"Increasing original amount of traffic with {(scaling_factor - 1) * 100:.2f}%")
    arrival_rates *= scaling_factor
    logging.info(f"Expected maximum sustainable increase: {(objective_value/scaling_factor - 1) * 100:.2f}%")

    logging.info(f"Maximizing capacity of the intersection with scaled traffic")
    fixed_time_schedule, phase_diagram, objective_value = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=arrival_rates, min_period_duration=30, max_period_duration=180,
        objective=ObjectiveEnum.max_capacity)

    # objective_value < 1 implies that the intersection is oversaturated for any traffic light controller.
    logging.info(f"Computed maximum sustainable increase in traffic: {(objective_value - 1) * 100:.2f}%")

    if print_fixed_time_schedule:
        logging.info(fixed_time_schedule)
        logging.info(phase_diagram)


if __name__ == "__main__":
    maximize_intersection_capacity()
