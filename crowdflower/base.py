# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class Attribute(object):

    def __init__(self, get_attr='_json', set_attr='_changes'):
        self.name = None
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
        super(_AttributeMeta, cls).__init__(what, bases, dict_)

        for name, attr in dict_.items():
            if isinstance(attr, Attribute):
                attr.name = name


_Base = _AttributeMeta('_Base', (object,), {})


class Base(_Base):
    """
    CrowdFlower Base type.
    """

    def __init__(self, data):
        self._json = data
        self._changes = {}

    def _update(self, updater):
        self._json.update(updater(self._changes))
        self._changes = {}
