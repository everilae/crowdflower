# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


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
