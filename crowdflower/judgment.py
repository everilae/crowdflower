# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base, Attribute, RoAttribute

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class JudgmentAggregate(Base):
    """
    CrowdFlower Judgment aggregate.

    :param client: Client instance that created this job instance
    :type client: crowdflower.client.Client
    :param job: Job instance that this Judgment belongs to
    :type job: crowdflower.job.Job
    :param data: Job JSON dictionary
    :type data: dict
    """

    _agreement = RoAttribute()
    _ids = RoAttribute()
    _state = RoAttribute()
    _updated_at = RoAttribute()

    def __init__(self, job, *args, **kwgs):
        self.job = job
        super(JudgmentAggregate, self).__init__(*args, **kwgs)

    def get_fields(self):
        """
        Get full aggregated field value dictionaries as a dictionary.

        :returns: dictionary of field, value items
        :rtype: dict
        """
        return {field: self._json[field] for field in self.job.fields.keys()}

    def get_aggregate(self, field):
        """
        Aggregated result for ``field``, chosen by CrowdFlower's aggregation
        logic.
        """
        return self._json[field]['agg']

    def get_results(self, field):
        """
        Full results for field ``field``

        :param field: Field name
        :returns: Results for field
        """
        return self._json[field]['res']


class Judgment(Base):
    """
    CrowdFlower Judgment.

    :param job: Job instance that this Judgment belongs to
    :type job: crowdflower.job.Job
    :param data: Job JSON dictionary
    :type data: dict
    :param client: Client instance that created this job instance
    :type client: crowdflower.client.Client
    """

    started_at = RoAttribute()
    created_at = RoAttribute()
    job_id = RoAttribute()
    contributor_id = RoAttribute()
    unit_id = RoAttribute()
    judgment = RoAttribute()
    external_type = RoAttribute()
    rejected = RoAttribute()
    ip = RoAttribute()
    id = RoAttribute()
    data = RoAttribute()
    unit_data = RoAttribute()
    trust = RoAttribute()
    worker_id = RoAttribute()
    worker_trust = RoAttribute()

    webhook_sent_at = Attribute()
    reviewed = Attribute()
    missed = Attribute()
    tainted = Attribute()
    country = Attribute()
    region = Attribute()
    city = Attribute()
    golden = Attribute()
    unit_state = Attribute()

    def __init__(self, job, data, client=None):
        self.job = job
        super(Judgment, self).__init__(data, client=client)
