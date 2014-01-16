# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base, RoAttribute

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

    def __init__(self, client, job, data):
        self._client = client
        self._job = job
        super(JudgmentAggregate, self).__init__(data)

    def get_fields(self):
        """
        Get full aggregated field value dictionaries as a dictionary.

        :returns: dictionary of field, value items
        :rtype: dict
        """
        return {field: self._json[field] for field in self._job.fields.keys()}

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

    :param client: Client instance that created this job instance
    :type client: crowdflower.client.Client
    :param job: Job instance that this Judgment belongs to
    :type job: crowdflower.job.Job
    :param data: Job JSON dictionary
    :type data: dict
    """

    #: Read only attributes
    RO_ATTRS = frozenset("""
        started_at
        created_at
        job_id
        contributor_id
        unit_id
        judgment
        external_type
        rejected
        ip
        id
        data
        """.strip().split())

    #: Read/write attributes
    RW_ATTRS = frozenset("""
        webhook_sent_at
        reviewed
        missed
        tainted
        country
        region
        city
        golden
        unit_state
        """.strip().split())

    def __init__(self, client, job, data):
        self._client = client
        self._job = job
        super(Judgment, self).__init__(data)
