# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base, Attribute, RoAttribute, WoAttribute
from operator import itemgetter
from .worker import Worker
from functools import wraps

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


def _command(f):
    """
    Helper function for creating repetitive :class:`Job` commands.
    """
    @wraps(f)
    def cmd(self):
        return self._client.jobs[self.id][f.__name__]()

    return cmd


class Job(Base):
    """
    CrowdFlower Job.

    Documentation for attributes can be found at
    https://success.crowdflower.com/hc/en-us/articles/202703435-CrowdFlower-API-Jobs-Resource-Attributes.

    :param data: Job JSON dictionary
    :type data: dict
    :param client: :class:`~.client.Client` instance that created this job instance
    :type client: crowdflower.client.Client
    """

    # RO attributes
    completed = RoAttribute()  # type: bool
    completed_at = RoAttribute()  # type: str
    created_at = RoAttribute()  # type: str
    crowd_costs = RoAttribute()  # type: float
    gold = RoAttribute()  # type: Dict[str, str]
    gold_per_assignment = RoAttribute()  # type: int
    golds_count = RoAttribute()  # type: int
    id = RoAttribute()  # type: int
    judgments_count = RoAttribute()  # type: int
    state = RoAttribute()  # type: str
    units_count = RoAttribute()  # type: int
    updated_at = RoAttribute()  # type: str

    # R/W attributes
    alias = Attribute()  # type: Optional[str]
    auto_order = Attribute()  # type: bool
    auto_order_threshold = Attribute()  # type: int
    auto_order_timeout = Attribute()  # type: Optional[int]
    cml = Attribute()  # type: str
    confidence_fields = Attribute()  # type: List[str]
    css = Attribute()  # type: str
    excluded_countries = Attribute()  # type: Optional[List[str]]
    expected_judgments_per_unit = Attribute()  # type: Optional[int]
    fields = Attribute()  # type: Dict[str, str]
    included_countries = Attribute()  # type: List[Dict[str, str]]
    instructions = Attribute()  # type: str
    js = Attribute()  # type: str
    judgments_per_unit = Attribute()  # type: int
    max_judgments_per_unit = Attribute()  # type: Optional[int]
    min_unit_confidence = Attribute()  # type: Optional[int]
    minimum_requirements = Attribute()  # type: Optional[dict]
    options = Attribute()  # type: Dict[str, ...]
    payment_cents = Attribute()  # type: float
    #problem = Attribute()  # type: str
    support_email = Attribute()  # type: str
    title = Attribute()  # type: str
    units_per_assignment = Attribute()  # type: int
    units_remain_finalized = Attribute()  # type: bool
    uri = WoAttribute()  # type: str
    variable_judgments_mode = Attribute()  # type: str
    webhook_uri = Attribute()  # type: Optional[str]

    # Undocumented/deprecated attributes, defaulted to RO, no idea of types...
    copied_from = RoAttribute()
    design_verified = RoAttribute()
    desired_requirements = RoAttribute()
    execution_mode = RoAttribute()
    language = RoAttribute()
    max_judgments_per_ip = RoAttribute()
    max_judgments_per_worker = RoAttribute()
    max_work_per_network = RoAttribute()
    minimum_account_age_seconds = RoAttribute()
    order_approved = RoAttribute()
    pages_per_assignment = RoAttribute()
    project_number = RoAttribute()
    public_data = RoAttribute()
    quiz_mode_enabled = RoAttribute()
    require_worker_login = RoAttribute()
    secret = RoAttribute()
    send_judgments_webhook = RoAttribute()
    worker_ui_remix = RoAttribute()

    def __init__(self, client=None, **data):
        super(Job, self).__init__(data, client=client)

    def _send_changes(self, changes):
        """
        Update :class:`Job` instance changes to server and return resulting
        reply JSON data.

        Normally subclasses need not implement both :meth:`_send_changes` and
        :meth:`update` methods, but :class:`Job`s require special data inspections
        that must be documented clearly.
        """
        return self._client.update_job(self.id, changes)

    def update(self):
        """
        Send updates made to this instance to CrowdFlower. Note that :attr:`title`,
        :attr:`instructions` and :attr:`cml` attributes must exist (either in the
        update or in the job already) for any changes to really persist, and so this
        method raises a :exc:`RuntimeError`, if any of them is missing.

           "At minimum, your job must have a valid title, instructions, and one
           *required* CML form element to be saved successfully." [1]_

        .. warning::

           The API will happily return a "valid" response when sent only the
           'instructions', but nothing will change on the server side without
           all three. The caller is responsible for providing valid CML.

        .. [1] https://success.crowdflower.com/hc/en-us/articles/202703435-CrowdFlower-API-Jobs-Resource-Attributes
           (Tue Jun 30 07:31:00 UTC 2015)

        :raises RuntimeError: if :attr:`title`, :attr:`instructions` or :attr:`cml`
                              is missing
        """
        for attr in {'title', 'instructions', 'cml'}:
            # Does a magic lookup to changes first, then the original json
            if not getattr(self, attr):
                raise RuntimeError(
                    "missing required attribute '{}'".format(attr))

        # calls Base.update, which calls _send_changes with changes dict
        super(Job, self).update()

    def upload(self, data, force=False):
        """
        Upload given data as JSON.

        :param data: Iterable of JSON serializable objects
        :type data: collections.abc.Iterable
        :param force: If True force adding units even if the columns do not
                      match existing data
        :type force: bool
        """
        self._client.upload_job(data, self.id, force=force)

    def upload_file(self, file, type_=None, force=False):
        """
        Upload a file like object or open a file for reading and upload.

        Caller is responsible for handling context on file like objects.
        Type must be provided with data as there is no information to make a
        guess from. If file like object provides text (unicode) data, it
        will be encoded to UTF-8 bytes.

        If explicit ``type_`` is not provided and the ``file`` is a string
        containing a filename to open, will make a guess with mimetypes.

        If type information is not given and guessing did not work,
        will raise a :exc:`ValueError`.

        Valid types are ``text/csv`` and ``application/json`` for ``.csv`` and
        ``.json`` respectively.

        :param file: A file like object or a filename string, contains UTF-8
                     encoded data
        :type file: str or file
        :param type_: Explicit type, required for file like objects
        :type type_: str
        :param force: If True force adding units even if the columns do not
                      match existing data
        :type force: bool
        :raises ValueError: if type information isn't provided and cannot
                            guess
        """
        self._client.upload_job_file(file, type_, self.id, force=force)

    def delete(self):
        """
        Delete this job, removing it from CrowdFlower. Calling :class:`Job`
        instance will be invalid after deletion and must not be used anymore.
        """
        self._client.delete_job(self.id)

    @property
    def judgment_aggregates(self):
        """
        List of :class:`~.judgment.JudgmentAggregate` instances of this :class:`Job`.

        .. warning::

           Judgments are paged with a maximum of 100 items per page. If your
           job has a lot of judgments – thousands or more – this will take
           a very VERY long time to finish when accessed for the first time.
           This might produce some nasty surprises, if :class:`Job` instances
           are inspected with :func:`inspect.getmembers` or some such.

        """
        try:
            return self._judgments_aggregates

        except AttributeError:
            # noinspection PyAttributeOutsideInit
            self._judgments_aggregates = list(
                self._client.get_judgmentaggregates(self))
            return self._judgments_aggregates

    def get_judgment(self, judgment_id):
        """
        Get single :class:`~.judgment.Judgment` for this :class:`Job`.
        """
        return self._client.get_judgment(self, judgment_id)

    def copy(self, all_units=False, gold=False):
        """
        Create a new job that is a copy of this job.

        :param all_units: If true, all of this job's units will be copied to the new job.
        :param gold: If true, only golden units will be copied to the new job.
        :returns: crowdflower.job.Job
        """
        return self._client.copy_job(self.id, all_units, gold)

    @property
    def channels(self):
        """
        List of enabled channels for this job.
        """
        return self._client.get_job_channels(self.id).get(
            'enabled_channels', [])

    @channels.setter
    def channels(self, channels):
        """
        Set enabled ``channels`` for this job.

        :type channels: list
        """
        self._client.set_job_channels(self.id, channels)

    @property
    def units(self):
        """
        List of :class:`~.unit.UnitPromise` instances of this :class:`Job`.
        """
        try:
            return self._units

        except AttributeError:
            # noinspection PyAttributeOutsideInit
            self._units = list(self._client.get_units(self))
            return self._units

    @_command
    def pause(self):
        """
        Temporarily stop judgments from coming in. A paused Job may
        ``resume``.
        """

    @_command
    def resume(self):
        """
        Resume a Job from ``pause`` at any time.
        """

    @_command
    def cancel(self):
        """
        Permanently ``cancel`` a Job, stopping any incoming judgments and
        refunding your account for unreceived judgments.
        """

    @_command
    def ping(self):
        """
        Check the status/progress of Job.
        """

    @_command
    def legend(self):
        """
        Display generated keys submitted with the form.
        """

    def get_worker(self, worker_id):
        """
        Get :class:`~.worker.Worker` ``worker_id`` bound to this :class:`Job`.
        """
        return Worker(self, client=self._client, id=worker_id)

    def launch(self, units_count, channels=('on_demand',)):
        """
        Order job with ``units_count`` at ``channels``.
        """
        return self._client.debit_order(self, units_count, channels)

    def get_results_report(self):
        """
        Download and parse JSON report containing aggregates and
        individual judgments as a list of :class:`Units <~.unit.Unit>`.
        :returns: list of crowdflower.unit.Unit
        """
        return self._client.get_report(self)

    # noinspection PyAttributeOutsideInit
    @property
    def tags(self):
        """
        List of tags.
        """
        try:
            return self._tags

        except AttributeError:
            self._tags = list(map(itemgetter('name'),
                                  self._client.get_job_tags(self.id)))
            return self._tags

    # noinspection PyAttributeOutsideInit
    @tags.setter
    def tags(self, tags):
        """
        List of tags.
        """
        self._client.set_job_tags(self.id, tags)
        self._tags = tags

    # noinspection PyAttributeOutsideInit
    def add_tag(self, tag):
        """
        Add tag.
        """
        self._client.add_job_tag(self.id, tag)
        try:
            self._tags.append(tag)

        except AttributeError:
            self._tags = [tag]

    def convert_test_questions(self):
        """
        Convert uploaded golden units to test questions.
        """
        self._client.convert_job_test_questions(self.id)
