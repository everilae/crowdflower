# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from inspect import getcallargs
from .base import RoAttribute, JobResource
from functools import wraps

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


def _command(f):
    """
    Helper function for handling Worker commands.
    """

    @wraps(f)
    def cmd(self, *args, **kwgs):
        callargs = getcallargs(f, self, *args, **kwgs)
        del callargs['self']

        self._client.send_worker_command(
            self.id, self.job.id, f.__name__, callargs,
        )

    return cmd


class Worker(JobResource):
    """
    CrowdFlower Worker.

    :param job: Job instance owning this Unit
    :type job: crowdflower.job.Job
    """

    id = RoAttribute()

    @_command
    def bonus(self, amount):
        """
        Pay Worker a bonus

        :param amount: Amount in cents
        :type amount: int
        """

    @_command
    def notify(self, message):
        """
        Notify a Worker contributor with the ``message``. The message
        appears in the workers dashboard.
        """

    def flag(self, reason):
        """
        Flags a worker with the ``reason``.
        """
        self._client.flag_worker(self.id, self.job.id, dict(flag=reason))

    def deflag(self, reason):
        """
        De-flags a worker with the ``reason``.
        """
        self._client.flag_worker(self.id, self.job.id, dict(deflag=reason))
