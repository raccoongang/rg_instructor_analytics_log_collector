"""
Collection of the discussion pipeline.
"""

import json
import logging

from opaque_keys.edx.keys import CourseKey, UsageKey
from xmodule.modulestore.django import modulestore

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import DiscussionActivity, LastProcessedLog, LogTable, \
    StudentStepCourse
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline


log = logging.getLogger(__name__)


class StudentStepPipeline(BasePipeline):
    """
    StudentStep stats Processor.
    """

    alias = 'student_step'
    supported_types = Events.NAVIGATIONAL_EVENTS

    def retrieve_last_date(self):
        """
        Fetch the moment of time daily enrollments were lastly updated.

        :return: DateTime or None
        """
        last_processed_log_table = LastProcessedLog.objects.filter(
            processor=LastProcessedLog.STUDENT_STEP
        ).first()

        return last_processed_log_table and last_processed_log_table.log_table.created

    def get_query(self):
        """
        Return list of the raw logs with type, that suitable for the given pipeline.
        """
        query = LogTable.objects.filter(message_type__in=self.supported_types)
        last_processed_log_date = self.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(created__gt=last_processed_log_date)

        return query.order_by('created')

    def get_units(self, event_body, event_type):
        current_unit = None
        target_unit = None
        subsection_id = event_body['id']

        sequential_locator = UsageKey.from_string(subsection_id)
        subsection_block = modulestore().get_item(sequential_locator, depth=1)

        if event_type in [Events.SEQ_GOTO, Events.SEQ_NEXT, Events.SEQ_PREV]:
            current_tab = event_body['old']
            target_tab = event_body['new']
            unit_children = subsection_block.get_children()

            try:
                current_unit = unit_children[current_tab-1].location.block_id
                target_unit = unit_children[target_tab-1].location.block_id
            except IndexError:
                pass

        elif event_type == Events.UI_SEQ_NEXT:
            try:
                # last unit in subsection
                current_unit = subsection_block.get_children()[-1].location.block_id
            except IndexError:
                pass

            is_next_subsection = False
            section_block = subsection_block.get_parent()
            for subsection in section_block.get_children():
                if subsection.location.block_id == subsection_block.location.block_id:
                    is_next_subsection = True
                    continue

                if is_next_subsection:
                    try:
                        # first unit in next subsection
                        target_unit = subsection.get_children()[0].location.block_id
                    except IndexError:
                        target_unit = ''
                        pass

                    break

            if target_unit is None:
                is_next_section = False
                for section in section_block.get_parent().get_children():
                    if section.location.block_id == section_block.location.block_id:
                        is_next_section = True
                        continue

                    if is_next_section:
                        try:
                            # first unit in next section -> first subsection
                            target_unit = section.get_children()[0].get_children()[0].location.block_id
                        except IndexError:
                            pass

                        break

        elif event_type == Events.UI_SEQ_PREV:
            try:
                # first unit in subsection
                current_unit = subsection_block.get_children()[0].location.block_id
            except IndexError:
                pass

            prev_subsection = None
            section_block = subsection_block.get_parent()

            for subsection in section_block.get_children():

                if subsection.location.block_id == subsection_block.location.block_id:
                    if prev_subsection:
                        try:
                            # last unit in prev_subsection
                            target_unit = prev_subsection.get_children()[-1].location.block_id
                        except IndexError:
                            pass
                    break

                prev_subsection = subsection

            if prev_subsection is None:
                prev_section = None

                for section in section_block.get_parent().get_children():
                    if section.location.block_id == section_block.location.block_id:
                        if prev_section:
                            try:
                                # last unit in prev_section -> last subsection
                                target_unit = prev_section.get_children()[-1].get_children()[-1].location.block_id
                            except IndexError:
                                pass
                        break

                    prev_section = section

        return current_unit, target_unit, subsection_id

    def format(self, record):
        """
        Format raw log to the internal format.
        """
        data = None
        event_body = json.loads(record.log_message)
        current_unit, target_unit, subsection_id = self.get_units(json.loads(event_body['event']), record.message_type)

        if current_unit and target_unit:
            data = {
                'event_type': record.message_type,
                'user_id': event_body['context']['user_id'],
                'course': CourseKey.from_string(event_body['context']['course_id']),
                'subsection_id': subsection_id,
                'current_unit': current_unit,
                'target_unit': target_unit,
                'log_time': record.log_time
            }

        return data

    def push_to_database(self, record, db_context):
        """
        Get or create StudentStepCourse.
        """
        StudentStepCourse.objects.get_or_create(**record)

    def update_last_processed_log(self, last_record):
        """
        Create or update last processed LogTable by Processor.
        """
        if last_record:
            LastProcessedLog.objects.update_or_create(processor=LastProcessedLog.STUDENT_STEP,
                                                      defaults={'log_table': last_record})
