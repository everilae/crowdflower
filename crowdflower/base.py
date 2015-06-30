# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from six import with_metaclass

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class Attribute(object):

    def __init__(self, name=None, get_attr='_json', set_attr='_changes'):
        self.name = name
        self.get_attr = get_attr
        self.set_attr = set_attr

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # Look in the 'set_attr' (holding possible temporary changes) first,
        # default to 'get_attr'.
        return getattr(instance, self.set_attr).get(
            self.name, getattr(instance, self.get_attr)[self.name])

    def __set__(self, instance, value):
        getattr(instance, self.set_attr)[self.name] = value


class RoAttribute(Attribute):

    def __set__(self, instance, value):
        raise AttributeError(
            "cannot change read only attribute '{}'".format(self.name))


class WoAttribute(Attribute):

    def __get__(self, instance, owner):
        if instance is None:
            return self

        raise AttributeError(
            "cannot read write only attribute '{}'".format(self.name))


class _AttributeMeta(type):
    """
    An evil hack that inspects certain types of attributes and sets
    values for them (names).
    """

    def __init__(cls, what, bases, dict_):
        for k, v in dict_.items():
            if isinstance(v, Attribute) and v.name is None:
                v.name = k

        super(_AttributeMeta, cls).__init__(what, bases, dict_)

    def __setattr__(cls, key, value):
        if isinstance(value, Attribute) and value.name is None:
            value.name = key

        super(_AttributeMeta, cls).__setattr__(key, value)


class Base(with_metaclass(_AttributeMeta, object)):
    """
    CrowdFlower Base type.

    :param data: JSON data
    :type data: dict
    :param client: CrowdFlower API client
    :type client: crowdflower.client.Client
    """

    def __init__(self, data, client=None):
        self._client = client
        self._json = data
        self._changes = {}

    def _send_changes(self, changes):
        """
        Sub classes must provide calls to send updates to server.
        """
        raise NotImplementedError(
            "abstract method '_send_changes' not implemented")

    def update(self):
        """
        Send changes to server and update instance with reply.
        """
        self._json.update(self._send_changes(self._changes))
        self._changes = {}

    @property
    def client(self):
        if not self._client:
            raise AttributeError("instance not bound to a client")

        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def __getitem__(self, item):
        """
        Allows job['item'] syntax for those preferring such things.
        """
        return self._changes.get(item, self._json[item])


class JobResource(Base):
    """
    Base class for all Job resources, like Worker, Judgment, Unit etc.

    :param job: :py:class:`Job <crowdflower.job.Job>` instance owning this JobResource
    :type job: crowdflower.job.Job
    :param client: :py:class:`Client <crowdflower.client.Client>` instance
    :type client: crowdflower.client.Client
    :param data: Unit JSON dictionary
    :type data: dict
    """

    def __init__(self, job, client=None, **data):
        super(JobResource, self).__init__(data, client=client)
        self.job = job


class Promise(object):
    """
    A promise that an crowdflower object will be available for querying
    attributes when needed.
    """

    _object = None

    def _get_object(self):
        """
        Abstract method.
        """
        raise NotImplementedError(
            "abstract method '_get_object' not implemented")

    def __getattr__(self, item):
        """
        Proxy attribute access to underlying object, if already fetched.
        """
        if self._object is None:
            self._object = self._get_object()

        return getattr(self._object, item)
