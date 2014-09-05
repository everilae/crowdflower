# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Attribute, RoAttribute, JobResource

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class JudgmentAggregate(JobResource):
    """
    CrowdFlower Judgment aggregate.

    :param job: :py:class:`Job <crowdflower.job.Job>` instance that this Judgment belongs to
    :type job: crowdflower.job.Job
    :param client: :py:class:`Client <crowdflower.client.Client>` instance
    :type client: crowdflower.client.Client
    :param data: Job JSON dictionary
    :type data: dict
    """

    agreement = RoAttribute(name='_agreement')
    ids = RoAttribute(name='_ids')
    state = RoAttribute(name='_state')
    updated_at = RoAttribute(name='_updated_at')

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

    @property
    def judgments(self):
        """
        List of Judgment instances for this aggregate.
        """
        try:
            return self._judgments

        except AttributeError:
            # noinspection PyAttributeOutsideInit
            self._judgments = [self._client.get_judgment(self.job, id_)
                               for id_ in self._ids]
            return self._judgments


class Judgment(JobResource):
    """
    CrowdFlower Judgment.

    :param job: :py:class:`Job <crowdflower.job.Job>` instance that this Judgment belongs to
    :type job: crowdflower.job.Job
    :param client: :py:class:`Client <crowdflower.client.Client>` instance
    :type client: crowdflower.client.Client
    :param data: Job JSON dictionary
    :type data: dict
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
