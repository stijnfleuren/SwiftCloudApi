<img src="https://www.swiftmobility.eu/swiftmobility.png" width="500"/>

# Swift Mobility Cloud API

## Introduction
This library provides a pure Python interface for the [Swift Mobility Cloud API](https://www.swiftmobility.eu/services). It works with Python versions 3.7 and above.

[Swift Mobility](https://www.swiftmobility.eu/) provides services for fully automated optimization of fixed-time schedules (traffic light schedules) in a matter of seconds, even for the most complex intersections. [Swift Mobility](https://www.swiftmobility.eu/) exposes a rest APIs and this library is intended to make it even easier for Python programmers to use.

## Usecases

### Smart traffic-light control

#### Completely adaptive traffic light control
The API can, in real-time, compute the optimal fixed-time schedule to best handle the current traffic situation; this enables truly smart and dynamic traffic light control that automatically adapts to the actual traffic situation. For example, by periodically computing the optimal fixed-time schedule and automatically converting it to a vehicle-actuated controller (e.g., using the green times as maximum green times and allowing green times to be terminated prematurely).

#### Automatically switch between control strategies
Low traffic and heavy traffic situations require a different control strategy. The API allows you to periodically quantify the current traffic situation in an automated manner, e.g., every 30 minutes. The result could be used to (automatically!) select the control strategy that best matches the current traffic situation; this would be truly smart traffic-light control!

### Monitoring
With the API you can quantify (in real-time) the amount of traffic arriving at the intersection to distinguish between low traffic, moderate traffic and heavy traffic situations. This information can be used to improve traffic management (e.g., redirect traffic to relieve highly congested parts of the network).

### Strategic decision making

#### Maintenance
Suppose traffic flow is not as smooth as desired at an intersection (e.g., experienced delays are large). With the API you can quantify if the intersection actually has sufficient capacity. If it does, then it might be sensible to reevaluate (and potentially update) such traffic-light controllers. In this way, maintenance efforts can be focused on the intersections where large improvements can be expected. If the capacity of the intersection is expected to be insufficient as well, then this might motivate infrastructural changes (see next usecase).

#### Updating infrastructure
Traffic situations may change overtime, e.g., due to urban development. Therefore, it is very important to periodically evaluate if any infrastructural changes (or policy changes by the government) are needed.

This is a very difficult decision to be made and it has high impact; quantitative support is really useful when making these decisions. With the API you can determine the maximum traffic increase that the infrastructure is able to handle under optimal traffic light control. This could be used to answer questions like: Is the capacity of the infrastructure (intersection) expected to still be sufficient in the upcoming 3 years?

## Installing
You can install the [Swift Mobility Cloud API](https://www.swiftmobility.eu/services) using:

```sh
$ pip install swift_cloud_py
```
## Getting the code

The code is hosted at https://github.com/stijnfleuren/SwiftCloudApi

Check out the latest development version anonymously with:

    $ git clone git://github.com/stijnfleuren/SwiftCloudApi.git
    $ cd swift_cloud_py

To install dependencies using pip, run:

    $ python -m pip install -Ur requirements.txt
    
To install dependencies using pipenv, run (from the swift_cloud_py/ folder):

    $ python -m pipenv install

## Getting started

### Credentials
To be able to connect to the Swift Mobility Cloud API you need credentials.
To this end, set the following two environment variables:
 - smc_api_key: this is the Swift Mobility Cloud API KEY
 - smc_secret_key: this is the Swift Mobility Cloud API Secret Key.

If you do not yet have these credentials, you can send a mail to cloud_api@swiftmobility.eu.

### How to load an intersection
Intersections and arrival rates can be loaded from a json file exported from Swift Mobility Desktop:

```python
import json
with open(smd_json_export, "r") as f:
    json_dict = json.load(f)

intersection = Intersection.from_json(intersection_dict=json_dict["intersection"])
arrival_rates = ArrivalRates.from_json(arrival_rates_dict=json_dict["arrival_rates"])
```

### How to create an intersection
Intersections can also be defined programmatically. 
#### Traffic light
Creating traffic lights:
```python
traffic_light = TrafficLight(capacity=1800, lost_time=2.2)
```
#### Signalgroups
Creating signalgroup:
```python
signalgroup =  SignalGroup(id="2", traffic_lights=[traffic_light1, traffic_light2], 
                           min_greenyellow=5, max_greenyellow=100, 
                           min_red=10, max_red=100, min_nr=1, max_nr=2)
```
#### Relations between signal groups
We can create traffic light control restrictions between signal groups. 

A conflict prevents two conflicting traffic streams from simultaneously crossing the intersection.
```python
conflict12 = Conflict(id1=signalgroup1.id, id2=signalgroup2.id, setup12=2, setup21=3)
```
A synchronous start ensures that two greenyellow intervals start at the same time; this can be used to create awareness
of partial conflicts, e.g., two opposing left movements (when driving on the right-hand side of the road).
```python
sync_start = SyncStart(from_id=signalgroup1.id, to_id=signalgroup2.id)
```
A greenyellow-lead can be used to create awareness of a partial conflict, e.g., to let turning traffic know that cyclists or pedestrians may cross the intersection.
```python
greenyellow_lead = GreenyellowLead(from_id=signalgroup1.id, to_id=signalgroup2.id, min_seconds=2, max_seconds=10)
```
An offset can be used to coordinate the start of two greenyellow intervals, which is useful to create green waves.
```python
offset = Offset(from_id=signalgroup1.id, to_id=signalgroup2.id, offset=5)
```
#### Intersections
Creating an intersection with all relevant traffic light control restrictions:
```python
intersection = Intersection(signalgroups=[signalgroup1, signalgroup2, signalgroup3],
                            conflicts=[conflict12, conflict13, conflict23])
```
Note: to optimize a fixed-time controller for two intersections with one controller, then this has to be 'modelled' as one intersection; the signalgroups (and conflicts etc.) of both intersections have to be provided to this Intersection object.

#### Arrival scenarios
Create an arrival scenario (arrival rates):
```python
morning_rates = ArrivalRates(id_to_arrival_rates={"2": [800, 700], "5": [300], "8": [350]})
```

### Storing and restoring intersections etc.
You can convert intersections and other objects to json; this is convenient to locally store this information for later 
re-use.
```python
json_serializable = intersection.to_json()
```
You can later restore this same object:
```python
intersection = Intersection.from_json(json_serializable)
```

### Optimizing fixed-time schedules
Optimize a fixed-time schedule for an intersection and a certain arrival rates:
```python
fixed_time_schedule, phase_diagram, objective_value = SwiftMobilityCloudApi.get_optimized_fts(
        intersection=intersection, arrival_rates=morning_rates, initial_queue_lengths=estimated_queue_lengths,
        objective=ObjectiveEnum.max_capacity)
```
We allow for several objectives:
* **ObjectiveEnum.min_delay**: Search for the fixed-time schedule that minimizes the expected (average) delay experienced by road users.
* **ObjectiveEnum.max_capacity**: Search for the fixed-time schedule that maximizes the largest increase in traffic (scaling factor) that the intersection can handle without becoming unstable/oversaturated. This gives an indication of how close to oversaturation the intersection is; an objective value of < 1 indicates that the intersection is oversaturated for all possible fixed-time schedules. This has usecases ranging from monitoring, smart traffic-light control and strategic decision making (see also swift_cloud_py/examples/maximizing_intersection_capacity)
* **ObjectiveEnum.min_period**: Search for the fixed-time schedule that has the smallest period duration (while still being stable).

You can print the fixed-time schedule in pretty format:
```python
print(fixed_time_schedule)
```
### computing phase diagram
When optimizing a fixed-time schedule, also the associated phase diagram is returned. However, you can also compute the phase diagram of any other fixed-time schedule:
```python
phase_diagram = SwiftMobilityCloudApi.get_phase_diagram(
    intersection=intersection, fixed_time_schedule=fixed_time_schedule)
```
The phase diagram can be printed in pretty format:
```python
print(phase_diagram)
```

### Tuning a fixed-time schedule
Traffic situations change throughout the day. This following function allows you to quickly adapt the green times of an existing fixed-time schedule to a new traffic situations.
```python
tuned_fixed_time_schedule, objective_value = SwiftMobilityCloudApi.get_tuned_fts(
    intersection=intersection, fixed_time_schedule=fixed_time_schedule, arrival_rates=midday_rates, 
    initial_queue_lengths=estimated_queue_lengths, objective=ObjectiveEnum.min_delay)
```
### Evaluating a fixed-time schedule
The expected performance of a fixed-time schedule can be computed as follows:
```python
kpis = SwiftMobilityCloudApi.evaluate_fts(intersection=intersection, fixed_time_schedule=fixed_time_schedule,
                                          arrival_rates=evening_rates)
```
These performance metrics can be printed with:
```python
print(kpis)
```

### Examples
On [github](https://github.com/stijnfleuren/SwiftCloudApi) you can find several examples in the folder swift_cloud_py/examples to get you started.

## License
MIT licence