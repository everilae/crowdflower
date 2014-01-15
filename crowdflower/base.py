# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class Base(object):
    """
    CrowdFlower Base type.
    """

    RO_ATTRS = frozenset()
    RW_ATTRS = frozenset()

    def __init__(self, data):
        self._json = data
        self._changes = {}

    def __setattr__(self, key, value):
        if key in self.RO_ATTRS:
            raise AttributeError(
                "cannot change read only attribute '{}'".format(key))

        elif key in self.RW_ATTRS:
            self._changes[key] = value

        else:
            super(Base, self).__setattr__(key, value)

    def __getattr__(self, item):
        if item in self.RO_ATTRS:
            return self._json[item]

        elif item in self.RW_ATTRS:
            return self._changes.get(item, self._json[item])

        raise AttributeError("'{}' object has no attribute '{}'".format(
            self.__class__.__name__,
            item
        ))

    def _update(self, data):
        self._json.update(data)
        self._changes = {}
