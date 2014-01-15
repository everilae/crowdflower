# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class JudgmentAggregate(Base):
    """
    CrowdFlower Judgment aggregate.
    """

    RO_ATTRS = frozenset("""
        _agreement
        _ids
        _state
        _updated_at
        """.strip().split())

    def __init__(self, client, job, data):
        """
        Initialize from given JSON dictionary.
        @param client: Client instance that created this job instance
        @type client: crowdflower.client.Client
        @param job: Job instance that this Judgment belongs to
        @type job: crowdflower.job.Job
        @param data: Job JSON dictionary
        @type data: dict
        """
        self._client = client
        self._job = job
        super(JudgmentAggregate, self).__init__(data)

    def get_aggregates(self):
        """
        Get full aggregated field value dictionaries as a dictionary.
        @return: dictionary of field, value items
        @rtype: dict
        """
        return {k: v for k, v in self._json.items()
                if isinstance(v, dict)}

    def get_aggregate(self, field):
        """
        Aggregated result for ``field``, chosen by CrowdFlower's aggregation
        logic.
        """
        return self._json[field]['agg']

    def get_results(self, field):
        """
        Full results for field ``field``

        @param field: Field name
        @return: Results for field
        """
        return self._json[field]['res']


class Judgment(Base):
    """
    CrowdFlower Judgment.
    """

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
        """
        Initialize from given JSON dictionary.
        @param client: Client instance that created this job instance
        @type client: crowdflower.client.Client
        @param job: Job instance that this Judgment belongs to
        @type job: crowdflower.job.Job
        @param data: Job JSON dictionary
        @type data: dict
        """
        self._client = client
        self._job = job
        super(Judgment, self).__init__(data)
