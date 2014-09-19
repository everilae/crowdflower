# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import RoAttribute, JobResource, Attribute

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class Order(JobResource):
    """
    CrowdFlower Order.

    Documentation for attributes can be found at
    http://success.crowdflower.com/customer/portal/articles/1288323-api-documentation#header_5

    An Order must be placed for a :class:`~.job.Job` to collect
    :class:`~.judgment.Judgment`.

    :param job: :class:`~.job.Job` instance owning this :class:`Unit`
    :type job: crowdflower.job.Job
    :param client: :class:`~.client.Client` instance
    :type client: crowdflower.client.Client
    :param data: Unit JSON dictionary
    :type data: dict
    """

    created_at = RoAttribute()
    id = RoAttribute()
    meta = RoAttribute()
    type = RoAttribute()
    updated_at = RoAttribute()
    user_id = RoAttribute()

    job_id = Attribute()
