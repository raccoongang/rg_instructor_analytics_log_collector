"""
Collection of the base pipelines.
"""

from abc import ABCMeta, abstractmethod
import json
import logging

from django.db.models import F
from opaque_keys.edx.keys import CourseKey

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import EnrollmentByDay, LastProcessedLog

log = logging.getLogger(__name__)


class BasePipeline(object):
    """
    Base Pipeline.

    NOTE: After implementing new pipeline, add it to the Processor.
    """

    __metaclass__ = ABCMeta

    """
    Readable name of the pipeline.
    """
    alias = None

    """
    Supported log types list.
    See:
    https://edx.readthedocs.io/projects/devdata/en/stable/internal_data_formats/event_list.html#event-list
    """
    supported_types = None

    @abstractmethod
    def retrieve_last_date(self):
        """
        Return date of the last processed record (or None for the first run).
        """
        pass

    def format(self, record):
        """
        Process raw message with different format to the single format.

        Note, if there no needs to change format set it as property, that equal to None.

        In case, when given record dosent relate to the given pipeline - return None.
        :param record:  raw log record.
        :return: dictionary with consistent structure.
        """
        return None

    def push_to_database(self, formatted_records):
        """
        Push to db final result.
        """


class EnrollmentPipeline(BasePipeline):
    """
    Enrollment stats Processor.
    """

    alias = 'enrollment'
    supported_types = Events.ENROLLMENT_EVENTS

    def retrieve_last_date(self):
        """
        Fetch the moment of time daily enrollments were lastly updated.

        :return: DateTime or None
        """
        last_processed_log_table = LastProcessedLog.objects.filter(
            processor=LastProcessedLog.ENROLLMENT
        ).first()

        return last_processed_log_table and last_processed_log_table.log_table.created

    def format(self, record):
        """
        Format raw log to the internal format.
        """
        event_body = json.loads(record.log_message)

        return {
            'is_enrolled': record.message_type == Events.USER_ENROLLED,
            'course': event_body['event']['course_id'],
            'log_time': record.log_time,
            'user': event_body['event']['user_id']
        }

    def push_to_database(self, record):
        """
        Save formatted message to the database.
        """
        course = CourseKey.from_string(record['course'])
        user_is_enrolled = record['is_enrolled']

        day_state, created = EnrollmentByDay.objects.get_or_create(
            course=course,
            day=record['log_time'].date(),
        )

        enrollment_for_the_last_day = EnrollmentByDay.objects.filter(
            course=course,
            day__lt=day_state.day
        ).order_by('day').last()

        enrollment_for_the_following_days = EnrollmentByDay.objects.filter(
            course=course,
            day__gt=day_state.day
        )

        if user_is_enrolled:
            day_state.enrolled += 1
        else:
            day_state.unenrolled += 1

        if enrollment_for_the_last_day:
            day_state.total = enrollment_for_the_last_day.total + day_state.enrolled - day_state.unenrolled
        else:
            day_state.total = day_state.enrolled - day_state.unenrolled
        day_state.save()

        if enrollment_for_the_following_days:
            total_delta = 1 if user_is_enrolled else -1
            enrollment_for_the_following_days.update(total=F('total') + total_delta)

    def update_last_processed_log(self, last_record):
        """
        Create or update last processed LogTable by Processor.
        """
        if last_record:
            LastProcessedLog.objects.update_or_create(processor=LastProcessedLog.ENROLLMENT,
                                                      defaults={'log_table': last_record})
