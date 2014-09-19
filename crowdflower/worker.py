# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from inspect import getcallargs
from .base import RoAttribute, JobResource
from functools import wraps, partial

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


def _command(f, method='post'):
    """
    Helper function for handling :class:`Worker` commands.
    """

    @wraps(f)
    def cmd(self, *args, **kwgs):
        """
        Self is :class:`Worker` instance.
        """
        callargs = getcallargs(f, self, *args, **kwgs)
        del callargs['self']

        self._client.send_worker_command(
            self,
            f.__name__, callargs,
            method
        )

    return cmd

# TODO: check which is correct:
# ruby-crowdflower Worker or
# http://success.crowdflower.com/customer/portal/articles/1553902-api-request-examples#header_4
_put_command = partial(_command, method='put')


class Worker(JobResource):
    """
    CrowdFlower Worker.

    :param job: :class:`~.job.Job` instance owning this :class:`Worker`
    :type job: crowdflower.job.Job
    :param client: :class:`~.client.Client` instance
    :type client: crowdflower.client.Client
    :param data: Attributes
    :type data: dict
    """

    id = RoAttribute()

    @_command
    def bonus(self, amount, reason=None):
        """
        Pay :class:`Worker` a bonus of ``amount`` cents. Optionally
        include a message stating the ``reason`` of the bonus.

        :param amount: Amount in cents
        :type amount: int
        :param reason: Include a message with the bonus
        :type reason: str
        """

    @_command
    def notify(self, message):
        """
        Notify a :class:`Worker` contributor with the ``message``. The message
        appears in the workers dashboard.

        :param message: Message to Worker
        :type message: str
        """

    @_put_command
    def flag(self, flag, persist=False):
        """
        Flags and prevents a :class:`Worker` from completing the :class:`~.job.Job`
        with the reason ``flag``. Existing :class:`judgments <crowdflower.judgment.Judgment>`
        will not be thrown away. If ``persist`` is se to ``True``, then the Worker is
        flagged out from all Jobs.

        :param flag: Flag reason
        :type flag: str
        :param persist: If True, flag in all Jobs (default False)
        :type persist: bool
        """

    @_put_command
    def deflag(self, deflag):
        """
        De-flags a :class:`Worker` with the reason ``deflag``.

        :param deflag: De-flag reason
        :type deflag: str
        """

    @_put_command
    def reject(self):
        """
        Prevents :class:`Worker` from completing :class:`jobs <crowdflower.job.Job>`
        and removes all :class:`judgments <crowdflower.judgment.Judgment>`.

        Care should be taken since a finalized :class:`~.job.Job` cannot collect new
        :class:`judgments <crowdflower.judgment.Judgment>` to replace the missing data.

        This feature is only available to Pro and Enterprise users.
        """
