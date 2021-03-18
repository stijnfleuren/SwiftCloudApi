from __future__ import annotations  # allows using intersection-typing inside intersection-class
import json
from typing import List, Union, Optional, Dict

from swift_cloud_py.entities.intersection.sg_relations import Conflict, SyncStart, Offset, GreenyellowLead
from swift_cloud_py.entities.intersection.signalgroup import SignalGroup


class Intersection:
    def __init__(self, signalgroups: List[SignalGroup], conflicts: List[Conflict],
                 sync_starts: Optional[List[SyncStart]] = None, offsets: Optional[List[Offset]] = None,
                 greenyellow_leads: Optional[List[GreenyellowLead]] = None) -> None:
        """
        intersection object containing information depending on intersection geometry and traffic light control
        strategy (e.g., sync starts etc.);

        Note: to optimize a fixed-time controller for two intersections with one controller, then this has to be
        'modelled' as one intersection; the signal groups (and conflicts etc.) of both intersections have to be
        provided to this Intersection object.
        :param signalgroups: list of signal group objects present at the intersection.
        :param conflicts: list of conflicts at the intersection.
        :param sync_starts: list of synchronous starts desired for this intersection.
        :param offsets: list of offsets desired for this intersection.
        :param greenyellow_leads: list of greenyellow_leads desired for this intersection.
        """
        self.signalgroups = signalgroups
        self.conflicts = conflicts
        self.sync_starts = sync_starts if sync_starts else []
        self.offsets = offsets if offsets else []
        self.greenyellow_leads = greenyellow_leads if greenyellow_leads else []
        self._validate()
        self._id_to_signalgroup = {signalgroup.id: signalgroup for signalgroup in signalgroups}

    @property
    def other_relations(self) -> List[Union[SyncStart, Offset, GreenyellowLead]]:
        other_relations = []
        other_relations.extend(self.sync_starts)
        other_relations.extend(self.offsets)
        other_relations.extend(self.greenyellow_leads)
        return other_relations

    def to_json(self):
        """get dictionary structure that can be stored as json with json.dumps()"""
        json_dict = dict(signalgroups=[signalgroup.to_json() for signalgroup in self.signalgroups],
                         conflicts=[conflict.to_json() for conflict in self.conflicts],
                         other_relations=[other_relation.to_json() for other_relation in self.other_relations])
        return json_dict

    def get_signalgroup(self, signalgroup_id: str):
        if signalgroup_id not in self._id_to_signalgroup:
            raise ValueError(f"signalgroup with id={signalgroup_id} does not exist")
        else:
            return self._id_to_signalgroup[signalgroup_id]

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

        # load other relations (synchronous starts, offsets and greenyellow_lead)
        sync_starts = []
        offsets = []
        greenyellow_leads = []
        for other_relation_dict in intersection_dict["other_relations"]:
            assert other_relation_dict["from_start_gy"] and other_relation_dict["to_start_gy"], \
                "besides conflicts, at the moment the cloud api can only handle synchronous starts, offsets " \
                "and greenyellow-leads."
            if other_relation_dict["min_time"] == other_relation_dict["max_time"]:
                if other_relation_dict["min_time"] == 0:  # sync start
                    sync_starts.append(SyncStart.from_json(sync_start_dict=other_relation_dict))
                else:  # offset
                    offsets.append(Offset.from_json(offset_dict=other_relation_dict))
            else:  # greenyellow-leads
                greenyellow_leads.append(GreenyellowLead.from_json(json_dict=other_relation_dict))
        return Intersection(signalgroups=signalgroups, conflicts=conflicts, sync_starts=sync_starts,
                            offsets=offsets, greenyellow_leads=greenyellow_leads)

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

    def _validate(self) -> None:
        """
        validate the arguments provided to this object
        :return: - (raises ValueError or TypeError if validation does not pass)
        """
        self._validate_types()
        self._validate_ids()
        self._validate_relations_per_pair()
        self._validate_setup_times()

    def _validate_types(self):
        """
        validate the datatypes of the arguments
        """
        # signalgroups
        if not isinstance(self.signalgroups, list):
            raise TypeError("signalgroups should be a list of SignalGroup objects")
        for signalgroup in self.signalgroups:
            if not isinstance(signalgroup, SignalGroup):
                raise TypeError("signalgroups should be a list of SignalGroup objects")

        # conflicts
        if not isinstance(self.conflicts, list):
            raise TypeError("conflicts should be a list of Conflict objects")
        for conflict in self.conflicts:
            if not isinstance(conflict, Conflict):
                raise TypeError("conflicts should be a list of Conflict objects")

        # sync starts
        if not isinstance(self.sync_starts, list):
            raise TypeError("sync_start should be a list of SyncStart objects")
        for sync_start in self.sync_starts:
            if not isinstance(sync_start, SyncStart):
                raise TypeError("sync_start should be a list of SyncStart objects")

        # offsets
        if not isinstance(self.offsets, list):
            raise TypeError("offsets should be a list of Offset objects")
        for offset in self.offsets:
            if not isinstance(offset, Offset):
                raise TypeError("offset should be a list of Coordination objects")

        # greenyellow_leads
        if not isinstance(self.greenyellow_leads, list):
            raise TypeError("greenyellow-lead should be a list of PreStart objects")
        for greenyellow_lead in self.greenyellow_leads:
            if not isinstance(greenyellow_lead, GreenyellowLead):
                raise TypeError("greenyellow-lead should be a list of PreStart objects")

    def _validate_ids(self):
        """
        validate ids used in signalgroups (uniqueness) and conflicts
        """
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

        for other_relation in self.other_relations:
            if other_relation.from_id not in unique_ids:
                raise ValueError(f"Unknown signalgoup id '{other_relation.from_id}' "
                                 f"used in object {other_relation.__class__}")
            if other_relation.to_id not in unique_ids:
                raise ValueError(f"Unknown signalgoup id '{other_relation.to_id}' "
                                 f"used in object {other_relation.__class__}")

    def _validate_relations_per_pair(self):
        # check uniqueness of the specified conflicts
        num_conflicts = len(self.conflicts)
        num_unique_conflicts = len({frozenset([conflict.id1, conflict.id2]) for conflict in self.conflicts})
        if num_conflicts != num_unique_conflicts:
            raise ValueError("Conflicts may not contain duplicate {id1, id2} pairs.")

        # validate that at most one relation is specified for each pair of signal groups
        unique_relations = {frozenset([relation.from_id, relation.to_id])
                            for relation in self.other_relations}
        unique_relations = unique_relations.union(
            {frozenset([conflict.id1, conflict.id2]) for conflict in self.conflicts})
        num_relations = len(self.other_relations) + len(self.conflicts)
        if num_relations != len(unique_relations):
            raise ValueError("Not allowed to specify multiple relations "
                             "(conflict, syncstart, offset, greenyellow_lead) for a single signal group pair.")

    def _validate_setup_times(self):
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
