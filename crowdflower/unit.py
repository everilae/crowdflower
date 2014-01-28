# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base, Attribute, RoAttribute

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class Unit(Base):
    """
    CrowdFlower Unit.

    :param job: Job instance owning this Unit
    :type job: crowdflower.job.Job
    :param data: Unit JSON dictionary
    :type data: dict
    :param client: CrowdFlower client
    :type client: crowdflower.client.Client
    """

    def __init__(self, job, data, client=None):
        self.job = job
        super(Unit, self).__init__(data, client=client)

    updated_at = RoAttribute()
    created_at = RoAttribute()
    judgments_count = RoAttribute()
    id = RoAttribute()
    unit_data = RoAttribute()

    job_id = Attribute()
    missed_count = Attribute()
    difficulty = Attribute()
    state = Attribute()
    data = Attribute()
    agreement = Attribute()

    def get_results(self):
        """
        Get unit results, if available.
        """
        return self._json.get('results')
