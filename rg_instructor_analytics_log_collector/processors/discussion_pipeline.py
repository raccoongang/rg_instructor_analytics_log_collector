"""
Collection of the discussion pipeline.
"""

import json
import logging

from opaque_keys.edx.keys import CourseKey

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import DiscussionActivity, DiscussionActivityByDay, \
    LastProcessedLog, LogTable
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline

log = logging.getLogger(__name__)


class DiscussionPipeline(BasePipeline):
    """
    Enrollment stats Processor.
    """

    alias = 'discussion'
    supported_types = Events.DISCUSSION_EVENTS

    def retrieve_last_date(self):
        """
        Fetch the moment of time daily enrollments were lastly updated.

        :return: DateTime or None
        """
        last_processed_log_table = LastProcessedLog.objects.filter(
            processor=LastProcessedLog.DISCUSSION_ACTIVITY
        ).first()

        return last_processed_log_table and last_processed_log_table.log_table.created

    def get_query(self):
        """
        Return list of the raw logs with type, that suitable for the given pipeline.
        """
        query = LogTable.objects.filter(message_type__in=Events.DISCUSSION_EVENTS)
        last_processed_log_date = self.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(created__gte=last_processed_log_date)

        return query.order_by('log_time')

    def format(self, record):
        """
        Format raw log to the internal format.
        """
        event_body = json.loads(record.log_message)

        return {
            'event_type': record.message_type,
            'user_id': event_body['context']['user_id'],
            'course': CourseKey.from_string(event_body['context']['course_id']),
            'category_id': event_body['event'].get('category_id'),
            'commentable_id': event_body['event']['commentable_id'],
            'discussion_id': event_body['event']['id'],
            'thread_type': event_body['event'].get('thread_type'),
            'log_time': record.log_time
        }

    def push_to_database(self, record, db_context):
        """
        Get or create Discussion Activities of User and by day.
        """
        disc_user_activity, disc_user_created = DiscussionActivity.objects.get_or_create(**record)
        if disc_user_created:
            disc_day_activity, disc_day_created = DiscussionActivityByDay.objects.get_or_create(
                course=disc_user_activity.course,
                day=disc_user_activity.log_time.date()
            )
            disc_day_activity.total = 1 if disc_day_created else (disc_day_activity.total + 1)
            disc_day_activity.save()

    def update_last_processed_log(self, last_record):
        """
        Create or update last processed LogTable by Processor.
        """
        if last_record:
            LastProcessedLog.objects.update_or_create(processor=LastProcessedLog.DISCUSSION_ACTIVITY,
                                                      defaults={'log_table': last_record})
