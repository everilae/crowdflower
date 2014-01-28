# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

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


#
# Workaround for py2 vs. py3 metaclass syntax differences.
#
# Python2:
#
# class Foo(object):
#     __metaclass__ = MetaClass
#     ...
#
# Python3:
#
# class Foo(metaclass=MetaClass):
#     ...
#
# Both python2 and python3:
_Base = _AttributeMeta('_Base', (object,), {})


class Base(_Base):
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

    def _update(self, updater):
        self._json.update(updater(self._changes))
        self._changes = {}

    @property
    def client(self):
        if not self._client:
            raise AttributeError("instance not bound to a client")

        return self._client

    @client.setter
    def client(self, value):
        self._client = value
