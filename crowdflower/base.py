# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class Attribute(object):

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance._changes.get(self.name,
                                     instance._json[self.name])

    def __set__(self, instance, value):
        instance._changes[self.name] = value


class RoAttribute(Attribute):

    def __set__(self, instance, value):
        raise AttributeError(
            "cannot change read only attribute '{}'".format(self.name))


class _AttributeMeta(type):

    def __init__(self, name, bases, dict_):
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

    def _update(self, data):
        self._json.update(data)
        self._changes = {}
