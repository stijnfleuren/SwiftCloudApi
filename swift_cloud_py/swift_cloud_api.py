import logging
import os
from typing import Tuple, Optional

import requests
from requests import Response

from swift_cloud_py.authentication.authentication import authenticate
from swift_cloud_py.common.errors import UnauthorizedException, BadRequestException, \
    UnknownCloudException
from swift_cloud_py.authentication.check_internet_connection import ensure_has_internet
from swift_cloud_py.entities.control_output.fixed_time_schedule import FixedTimeSchedule
from swift_cloud_py.entities.control_output.phase_diagram import PhaseDiagram
from swift_cloud_py.entities.intersection.intersection import Intersection
from swift_cloud_py.entities.scenario.arrival_rates import ArrivalRates
from swift_cloud_py.entities.scenario.queue_lengths import QueueLengths
from swift_cloud_py.enums import ObjectiveEnum

# allows using a test version of the api hosted at a different url (for testing purposes).
CLOUD_API_URL = os.environ.get("smc_api_url", "https://cloud-api.swiftmobility.eu")


def check_status_code(response: Response) -> None:
    """
    check status code returned by rest-api call; raises appropriate error if status code indicates that the call was
    not succesfull.
    """
    if response.status_code in [400]:
        raise BadRequestException(str(response.json()))
    elif response.status_code in [401]:
        raise UnauthorizedException("JWT validation failed: Missing or invalid credentials")
    elif response.status_code in [402]:
        raise UnauthorizedException("Insufficient credits (cpu seconds) left.")
    elif response.status_code in [403]:
        raise UnauthorizedException("Forbidden.")
    elif response.status_code in [426]:
        raise UnauthorizedException(f"The cloud api is still in the beta phase; this means it might change. "
                                    f"Message from cloud: {response.json()['msg']}.")
    elif response.status_code in [504]:
        raise TimeoutError
    elif response.status_code != 200:
        raise UnknownCloudException


class SwiftMobilityCloudApi:
    """
    Class to communicate with the cloud-api of swift mobility (and automating authentication).
    Using this class simplifies the communication with the cloud-api (compared to using the rest-api's directly)
    """
    _authentication_token: str = None  # this token is updated by the @authenticate decorator

    @classmethod
    @ensure_has_internet
    @authenticate
    def get_optimized_fts(cls, intersection: Intersection, arrival_rates: ArrivalRates,
                          horizon: float = 2.0,
                          min_period_duration: float = 0.0, max_period_duration: float = 180,
                          objective: ObjectiveEnum = ObjectiveEnum.min_delay,
                          initial_queue_lengths: Optional[QueueLengths] = None,
                          ) -> Tuple[FixedTimeSchedule, PhaseDiagram, float]:
        """
        Optimize a fixed-time schedule
        :param intersection: intersection for which to optimize the fts (contains signalgroups, conflicts and more)
        :param arrival_rates: arrival rates in personal car equivalent per hour (PCE/h)
        :param horizon: time period of interest in hours.
        :param min_period_duration: minimum period duration of the fixed-time schedule in seconds
        :param max_period_duration: minimum period duration of the fixed-time schedule in seconds
        :param objective: what kpi (key performance indicator) to optimize. The following options are available:
         - ObjectiveEnum.min_delay: minimize the delay experienced by road users arriving at the intersection during
         the next 'horizon' hours. The initially waiting traffic is modeled as implicitly by increasing the
         arrival rate by initial_queue_length / horizon PCE/h; this implies that we assume that this traffic is arriving
         (evenly spread) during the horizon.
         - ObjectiveEnum.min_period: search for the fixed-time schedule with the smallest period duration for which
         all traffic lights are 'stable', i.e., the greenyellow interval is large enough so that the amount of traffic
          that  can (on average) depart during the horizon exceeds the traffic that arrives during
          the horizon (+ initially waiting traffic).
         - ObjectiveEnum.max_capacity: search for the fixed-time schedule that can handle the largest (percentual)
         increase in traffic (including the initial amount of traffic), i.e., the largest percentual increase in traffic
          for which all traffic lights are 'stable' (see also ObjectiveEnum.min_period).
        :param initial_queue_lengths: initial amount of traffic waiting at each of the traffic lights; if None, then we
        assume no initial traffic.
        :return: fixed-time schedule, associated phase diagram and the objective value
        (minimized delay, minimized period, or maximum percentual increase in traffic divided by 100, e.g. 1 means
        currently at the verge of stability)
        """
        assert horizon >= 1, "horizon should exceed one hour"
        if initial_queue_lengths is None:
            # assume no initial traffic
            initial_queue_lengths = QueueLengths({signalgroup.id: [0] * len(signalgroup.traffic_lights)
                                                  for signalgroup in intersection.signalgroups})

        for signalgroup in intersection.signalgroups:
            assert signalgroup.id in arrival_rates.id_to_arrival_rates, \
                f"arrival rate(s) must be specified for signalgroup {signalgroup.id}"
            assert len(arrival_rates.id_to_arrival_rates[signalgroup.id]) == len(signalgroup.traffic_lights), \
                f"arrival rate(s) must be specified for all traffic lights of signalgroup {signalgroup.id}"

            assert signalgroup.id in initial_queue_lengths.id_to_queue_lengths, \
                f"initial_queue_lengths(s) must be specified for signalgroup {signalgroup.id}"
            assert len(initial_queue_lengths.id_to_queue_lengths[signalgroup.id]) == len(signalgroup.traffic_lights), \
                f"initial_queue_lengths(s) must be specified for all traffic lights of signalgroup {signalgroup.id}"

        endpoint = f"{CLOUD_API_URL}/fts-optimization"
        headers = {'authorization': 'Bearer {0:s}'.format(cls._authentication_token)}

        # rest-api call
        try:
            # assume that the traffic that is initially present arrives during the horizon.
            corrected_arrival_rates = arrival_rates + initial_queue_lengths / horizon
            json_dict = dict(
                intersection=intersection.to_json(),
                arrival_rates=corrected_arrival_rates.to_json(),
                min_period_duration=min_period_duration,
                max_period_duration=max_period_duration,
                objective=objective.value
            )
            logging.debug(f"calling endpoint {endpoint}")
            r = requests.post(endpoint, json=json_dict, headers=headers)
            logging.debug(f"finished calling endpoint {endpoint}")
        except requests.exceptions.ConnectionError:
            raise UnknownCloudException("Connection with swift mobility cloud api could not be established")

        # check for errors
        check_status_code(response=r)

        # parse output
        output = r.json()
        objective_value = output["obj_value"]
        fixed_time_schedule = FixedTimeSchedule.from_json(output["fixed_time_schedule"])
        phase_diagram = PhaseDiagram.from_json(output["phase_diagram"])

        return fixed_time_schedule, phase_diagram, objective_value

    @classmethod
    @ensure_has_internet
    @authenticate
    def get_phase_diagram(cls, intersection: Intersection, fixed_time_schedule: FixedTimeSchedule) -> PhaseDiagram:
        """
        Get the phase diagram specifying the order in which the signal groups have their greenyellow intervals
        in the fixed-time schedule
        :param intersection: intersection for which to optimize the fts (contains signalgroups, conflicts and more)
        :param fixed_time_schedule: fixed-time schedule for which we want to retrieve the phase diagram.
        :return:
        """
        endpoint = f"{CLOUD_API_URL}/phase-diagram-computation"
        headers = {'authorization': 'Bearer {0:s}'.format(cls._authentication_token)}

        # rest-api call
        try:
            json_dict = dict(
                intersection=intersection.to_json(),
                greenyellow_intervals=fixed_time_schedule.to_json()["greenyellow_intervals"],
                period=fixed_time_schedule.to_json()["period"]
            )
            logging.debug(f"calling endpoint {endpoint}")
            r = requests.post(endpoint, json=json_dict, headers=headers)
            logging.debug(f"finished calling endpoint {endpoint}")
        except requests.exceptions.ConnectionError:
            raise UnknownCloudException("Connection with swift mobility cloud api could not be established")

        # check for errors
        check_status_code(response=r)
        output = r.json()

        # parse output
        phase_diagram = PhaseDiagram.from_json(output["phase_diagram"])
        return phase_diagram
