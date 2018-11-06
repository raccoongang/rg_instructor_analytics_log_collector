"""
Collection of the video views pipeline.
"""
import json
import logging

from opaque_keys.edx.keys import CourseKey

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import LastProcessedLog, LogTable, VideoViewsByBlock, \
    VideoViewsByDay, VideoViewsByUser
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline

log = logging.getLogger(__name__)


class VideoViewsPipeline(BasePipeline):
    """
    VideoViews stats Processor.
    """

    alias = 'video_views'
    supported_types = Events.VIDEO_VIEW_EVENTS

    def retrieve_last_date(self):
        """
        Fetch the moment of time daily video views were lastly updated.

        :return: DateTime or None
        """
        last_processed_log_table = LastProcessedLog.objects.filter(
            processor=LastProcessedLog.VIDEO_VIEWS
        ).first()

        return last_processed_log_table and last_processed_log_table.log_table.created

    def get_query(self):
        """
        Return list of the raw logs with type, that suitable for the given pipeline.
        """
        query = LogTable.objects.filter(message_type__in=Events.VIDEO_VIEW_EVENTS)
        last_processed_log_date = self.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(created__gte=last_processed_log_date)

        return query.order_by('log_time')

    def format(self, record):
        """
        Format raw log to the internal format.
        """
        event_body = json.loads(record.log_message)
        event_body_detail = json.loads(event_body['event'])
        return {
            'course_id': event_body['context']['course_id'],
            'user_id': event_body['context']['user_id'],
            'block_id': event_body_detail['id'],
            'viewed_time': event_body_detail['currentTime'],
            'is_video_completed': True if record.message_type == Events.USER_FINISHED_WATCH_VIDEO else False,
            'log_time': record.log_time,
            'event_type': record.message_type
        }

    def push_to_database(self, record, db_context):
        """
        Save Video Views info to the database.
        """
        course = CourseKey.from_string(record['course_id'])
        user_id = record['user_id']

        if record['event_type'] == Events.USER_STARTED_VIEW_VIDEO:
            video_views_by_day, created_video_day = VideoViewsByDay.objects.get_or_create(
                course=course,
                video_block_id=record['block_id'],
                day=record['log_time'].date(),
            )
            list_users_ids = video_views_by_day.users_ids.split(',') if video_views_by_day.users_ids else []

            if created_video_day:
                video_views_by_day.users_ids = user_id
                video_views_by_day.total = 1
                video_views_by_day.save()

            elif str(user_id) not in list_users_ids:
                video_views_by_day.users_ids += ',{}'.format(user_id)
                video_views_by_day.total += 1
                video_views_by_day.save()
        else:
            video_views_by_user, created_video_user = VideoViewsByUser.objects.get_or_create(
                course=course,
                user_id=record['user_id'],
                video_block_id=record['block_id'],
            )

            if not video_views_by_user.is_completed:
                try:
                    viewed_time = int(record['viewed_time'])
                except ValueError:
                    viewed_time = 0

                if viewed_time >= int(video_views_by_user.viewed_time):
                    video_views_by_user.viewed_time = viewed_time
                    video_views_by_user.is_completed = record['is_video_completed']
                    video_views_by_user.save()

                video_views_by_block, _ = VideoViewsByBlock.objects.get_or_create(
                    course=course,
                    video_block_id=record['block_id'],
                )

                if created_video_user:
                    video_views_by_block.count_part_viewed += 1
                    video_views_by_block.save()

                if video_views_by_user.is_completed:
                    video_views_by_block.count_full_viewed += 1
                    video_views_by_block.video_duration = video_views_by_user.viewed_time
                    video_views_by_block.save()

    def update_last_processed_log(self, last_record):
        """
        Create or update last processed LogTable by Processor.
        """
        if last_record:
            LastProcessedLog.objects.update_or_create(processor=LastProcessedLog.VIDEO_VIEWS,
                                                      defaults={'log_table': last_record})
