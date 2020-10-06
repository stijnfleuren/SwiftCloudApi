from __future__ import annotations  # allows using intersection-typing inside intersection-class
import json
from typing import List, Union, Optional, Dict

from swift_cloud_py.entities.intersection.sg_relations import Conflict, SyncStart, Coordination, PreStart
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup


class Intersection:
    def __init__(self, signalgroups: List[SignalGroup], conflicts: List[Conflict],
                 sync_starts: Optional[List[SyncStart]] = None, coordinations: Optional[List[Coordination]] = None,
                 prestarts: Optional[List[PreStart]] = None) -> None:
        """
        intersection object containing information depending on intersection geometry and traffic light control
        strategy (e.g., sync starts etc.);

        Note: to optimize a fixed-time controller for two intersections with one controller, then this has to be
        'modelled' as one intersection; the signal groups (and conflicts etc.) of both intersections have to be
        provided to this Intersection object.
        :param signalgroups: list of signal group objects present at the intersection.
        :param conflicts: list of conflicts at the intersection.
        :param sync_starts: list of synchronous starts desired for this intersection.
        :param coordinations: list of coordinations desired for this intersection.
        :param prestarts: list of prestarts desired for this intersection.
        """
        self.signalgroups = signalgroups
        self.conflicts = conflicts
        self.sync_starts = sync_starts if sync_starts else []
        self.coordinations = coordinations if coordinations else []
        self.prestarts = prestarts if prestarts else []
        self.validate()

    @property
    def other_relations(self) -> List[Union[SyncStart, Coordination, PreStart]]:
        other_relations = []
        other_relations.extend(self.sync_starts)
        other_relations.extend(self.coordinations)
        other_relations.extend(self.prestarts)
        return other_relations

    def to_json(self):
        """get dictionary structure that can be stored as json with json.dumps()"""
        json_dict = dict(signalgroups=[signalgroup.to_json() for signalgroup in self.signalgroups],
                         conflicts=[conflict.to_json() for conflict in self.conflicts],
                         other_relations=[other_relation.to_json() for other_relation in self.other_relations])
        return json_dict

    @staticmethod
    def from_json(intersection_dict: Dict) -> Intersection:
        """
        Loading intersection from json (expected same json structure as generated with to_json)
        :param intersection_dict:
        :return: intersection object
        """
        # load signal groups
        signalgroups = [SignalGroup.from_json(signalgroup_dict=signalgroup_dict)
                        for signalgroup_dict in intersection_dict["signalgroups"]]

        # load conflicts
        conflicts = [Conflict.from_json(conflict_dict=conflict_dict)
                     for conflict_dict in intersection_dict["conflicts"]]

        # load other relations (synchronous starts, coordinations and prestarts)
        sync_starts = []
        coordinations = []
        prestarts = []
        for other_relation_dict in intersection_dict["other_relations"]:
            assert other_relation_dict["from_start_gy"] and other_relation_dict["to_start_gy"], \
                "besides conflicts, at the moment the cloud api can only handle synchronous starts, coordinations " \
                "and prestarts."
            if other_relation_dict["min_time"] == other_relation_dict["max_time"]:
                if other_relation_dict["min_time"] == 0:  # sync start
                    sync_starts.append(SyncStart.from_json(sync_start_dict=other_relation_dict))
                else:  # coordination
                    coordinations.append(Coordination.from_json(coordination_dict=other_relation_dict))
            else:  # prestart
                prestarts.append(PreStart.from_json(pre_start_dict=other_relation_dict))
        return Intersection(signalgroups=signalgroups, conflicts=conflicts, sync_starts=sync_starts,
                            coordinations=coordinations, prestarts=prestarts)

    @staticmethod
    def from_swift_mobility_export(json_path) -> Intersection:
        """
        Loading intersection from json-file exported from Swift Mobility Desktop
        :param json_path: path to json file
        :return: intersection object
        """
        with open(json_path, "r") as f:
            json_dict = json.load(f)

        # the json structure conforms with the expected structure; it only contains additional information (which is
        # ignored).
        return Intersection.from_json(intersection_dict=json_dict["intersection"])

    def validate(self) -> None:
        """
        # validate all inputs
        :return: - (raises error if validation does not pass)
        """
        assert isinstance(self.signalgroups, list), "signalgroups should be a list of SignalGroup objects"
        for signalgroup in self.signalgroups:
            assert isinstance(signalgroup, SignalGroup), "signalgroups should be a list of SignalGroup objects"
        assert isinstance(self.conflicts, list), "conflicts should be a list of Conflict objects"
        for conflict in self.conflicts:
            assert isinstance(conflict, Conflict), "conflicts should be a list of Conflict objects"
        assert isinstance(self.sync_starts, list), "sync_start should be a list of SyncStart objects"
        for sync_start in self.sync_starts:
            assert isinstance(sync_start, SyncStart), "sync_start should be a list of SyncStart objects"
        assert isinstance(self.coordinations, list), "coordination should be a list of Coordination objects"
        for coordination in self.coordinations:
            assert isinstance(coordination, Coordination), "coordination should be a list of Coordination objects"
        assert isinstance(self.prestarts, list), "prestart should be a list of PreStart objects"
        for prestart in self.prestarts:
            assert isinstance(prestart, PreStart), "prestart should be a list of PreStart objects"

        # validate unique ids
        ids = [signalgroup.id for signalgroup in self.signalgroups]
        unique_ids = set(ids)
        if len(unique_ids) != len(ids):
            raise ValueError("signalgroup ids should be unique")

        # check existence ids used in conflicts
        for conflict in self.conflicts:
            if conflict.id1 not in unique_ids:
                raise ValueError(f"Unknown signalgoup id '{conflict.id1}' used in conflict")
            if conflict.id2 not in unique_ids:
                raise ValueError(f"Unknown signalgoup id '{conflict.id2}' used in conflict")

        # check uniqueness of the specified conflicts
        num_conflicts = len(self.conflicts)
        num_unique_conflicts = len({frozenset([conflict.id1, conflict.id2]) for conflict in self.conflicts})
        if num_conflicts != num_unique_conflicts:
            raise ValueError("Conflicts may not contain duplicate {id1, id2} pairs.")

        # validate that at most one relation is specified for each pair of signal groups
        for other_relation in self.other_relations:
            if other_relation.from_id not in unique_ids:
                raise ValueError(f"Unknown signalgoup id '{other_relation.from_id}' "
                                 f"used in object {other_relation.__class__}")
            if other_relation.to_id not in unique_ids:
                raise ValueError(f"Unknown signalgoup id '{other_relation.to_id}' "
                                 f"used in object {other_relation.__class__}")

            unique_relations = {frozenset([relation.from_id, relation.to_id])
                                for relation in self.other_relations}
            unique_relations = unique_relations.union(
                {frozenset([conflict.id1, conflict.id2]) for conflict in self.conflicts})
            num_relations = len(self.other_relations) + len(self.conflicts)
            if num_relations != len(unique_relations):
                raise ValueError("Not allowed to specify multiple relations "
                                 "(conflict, syncstart, coordination, prestart) for a single signal group pair.")

        # validate setup times are not too negative
        id_to_signalgroup = {signalgroup.id: signalgroup for signalgroup in self.signalgroups}
        for conflict in self.conflicts:
            # this we catch in another validation step
            if conflict.id1 not in id_to_signalgroup or conflict.id2 not in id_to_signalgroup:
                continue
            signalgroup1 = id_to_signalgroup[conflict.id1]
            signalgroup2 = id_to_signalgroup[conflict.id2]
            if signalgroup1.min_greenyellow + conflict.setup12 <= 0:
                raise ValueError(f"setup12 plus min_greenyellow of signal group sg1 must be strictly positive, "
                                 f"which is not satisfied for signal groups sg1='{conflict.id1}' "
                                 f"and sg2='{conflict.id2}'.")
            if signalgroup2.min_greenyellow + conflict.setup21 <= 0:
                raise ValueError(f"setup21 plus min_greenyellow of signal group sg2 must be strictly positive, "
                                 f"which is not satisfied for signal groups sg1='{conflict.id1}' "
                                 f"and sg2='{conflict.id2}'.")
