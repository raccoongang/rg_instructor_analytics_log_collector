"""
Collection of the enrollment pipeline.
"""

import json
import logging

from django.db.models import Q
from opaque_keys.edx.keys import CourseKey

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import EnrollmentByDay, EnrollmentByUser, LastProcessedLog, LogTable
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline

log = logging.getLogger(__name__)


class EnrollmentPipeline(BasePipeline):
    """
    Enrollment stats Processor.
    """

    alias = 'enrollment'
    supported_types = [
        '/admin/student/courseenrollment/',
    ] + Events.ENROLLMENT_EVENTS

    def retrieve_last_date(self):
        """
        Fetch the moment of time daily enrollments were lastly updated.

        :return: DateTime or None
        """
        last_processed_log_table = LastProcessedLog.objects.filter(
            processor=LastProcessedLog.ENROLLMENT
        ).first()

        return last_processed_log_table and last_processed_log_table.log_table.created

    def get_query(self):
        """
        Return list of the raw logs with type, that suitable for the given pipeline.
        """
        type_request = None

        for pipeline_type in self.supported_types:
            if type_request is None:
                type_request = Q(message_type__contains=pipeline_type)
            else:
                type_request |= Q(message_type__contains=pipeline_type)

        query = LogTable.objects.filter(type_request)
        last_processed_log_date = self.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(created__gte=last_processed_log_date)

        return query.order_by('log_time')

    def _format_as_edx_event(self, record):
        """
        Format raw edx event to internal format.
        """
        event_body = json.loads(record.log_message)
        return {
            'is_enrolled': record.message_type == Events.USER_ENROLLED,
            'course': event_body['event']['course_id'],
            'user': event_body['event']['user_id']
        }

    def _format_request_event(self, record):
        """
        Format raw request event to internal format.
        """
        event_body = json.loads(record.log_message)
        try:
            event_info = json.loads(event_body['event'])['POST']
            return {
                'is_enrolled': event_info.get('is_active', ['off'])[0] == 'on',
                'course': event_info['course_id'][0],
                'user': event_info['user'][0]
            }
        except (IndexError, KeyError, ValueError) as e:
            log.debug('Can not parse enrollment information from the request event. {}, {}'.format(
                event_body, repr(e)
            ))
            return None

    @property
    def ordered_fields(self):
        """
        Ordering fields list.
        """
        return ['log_time', 'course']

    def format(self, record):
        """
        Format raw log to the internal format.
        """
        if record.message_type in Events.ENROLLMENT_EVENTS:
            result = self._format_as_edx_event(record)
        else:
            result = self._format_request_event(record)

        if result:
            result['log_time'] = record.log_time
        return result

    def aggregate(self, records):
        """
        Agregate messages by date and course.
        """
        date = None
        course = None
        users = []
        for r in records:
            if date is not None and (r['log_time'].date() != date or course != r['course']):
                yield ((date, course), users)
            date = r['log_time'].date()
            course = r['course']
            users.append((r['user'], r['is_enrolled']))
        yield ((date, course), users)

    def load_database_contex(self, aggregated_records):
        """
        Load last collected stat about course enrollment and user enrollment.
        """
        (__, course), users = aggregated_records
        user_query = [Q(student=user) for user, _ in users]
        user_query_result = user_query[0]
        for q in user_query[1:]:
            user_query_result |= q

        course_key = CourseKey.from_string(course)
        user_query_result &= Q(course=course_key)

        return (
            EnrollmentByUser.objects.filter(user_query_result).all(),
            EnrollmentByDay.objects.filter(course=course_key).first()
        )

    def push_to_database(self, aggregated_records, db_context):
        """
        Save agregated message to the database.
        """
        user_info, course_info = db_context
        (date, course), users = aggregated_records
        total = 0
        enrollment = 0
        unenrollemnt = 0
        if course_info:
            total = course_info.total
            if date == course_info.day:
                enrollment = course_info.enrolled
                unenrollemnt = course_info.unenrolled

        users_state = {uf.student: uf.is_enrolled for uf in user_info or []}
        for user, is_enrolled in users:
            if user in users_state and users_state[user] == is_enrolled:
                continue
            users_state[user] = is_enrolled
            if is_enrolled:
                enrollment += 1
                total += 1
            else:
                unenrollemnt += 1
                total -= 1

        course_key = CourseKey.from_string(course)
        EnrollmentByDay.objects.update_or_create(
            course=course_key,
            day__day=date.day,
            day__month=date.month,
            day__year=date.year,
            defaults={
                'total': total,
                'enrolled': enrollment,
                'unenrolled': unenrollemnt,
                'day': date,
            }
        )

        for user, state in users_state.items():
            EnrollmentByUser.objects.update_or_create(
                course=course_key,
                student=user,
                defaults={
                    'is_enrolled': state
                }
            )

    def update_last_processed_log(self, last_record):
        """
        Create or update last processed LogTable by Processor.
        """
        if last_record:
            LastProcessedLog.objects.update_or_create(processor=LastProcessedLog.ENROLLMENT,
                                                      defaults={'log_table': last_record})
