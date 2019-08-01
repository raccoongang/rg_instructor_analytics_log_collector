"""
Collection of the discussion pipeline.
"""

import json
import logging

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey

from rg_instructor_analytics_log_collector.constants import Events
from rg_instructor_analytics_log_collector.models import LastProcessedLog, StudentStepCourse
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError

log = logging.getLogger(__name__)


class StudentStepPipeline(BasePipeline):
    """
    StudentStep stats Processor.
    """

    alias = 'student_step'
    supported_types = Events.NAVIGATIONAL_EVENTS
    processor_name = LastProcessedLog.STUDENT_STEP

    def get_units(self, event_body, event_type):
        """
        Get info of student path by units.
        """
        current_unit = None
        target_unit = None
        subsection_id = event_body['id']

        try:
            sequential_locator = UsageKey.from_string(subsection_id)
        except InvalidKeyError as err:
            logging.info('InvalidKeyError (subsection_id - "{}") {}'.format(subsection_id, err))
            return current_unit, target_unit, subsection_id

        try:
            subsection_block = modulestore().get_item(sequential_locator, depth=1)
        except ItemNotFoundError as err:
            logging.info('Item {} not found.'.format(err))
            return current_unit, target_unit, subsection_id

        if event_type in [Events.SEQ_GOTO, Events.SEQ_NEXT, Events.SEQ_PREV]:
            current_tab = event_body['old']
            target_tab = event_body['new']
            unit_children = subsection_block.get_children()

            try:
                current_unit = unit_children[current_tab - 1].location.block_id
                target_unit = unit_children[target_tab - 1].location.block_id
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
        event_body = json.loads(record.log_message)

        try:
            course = CourseKey.from_string(event_body['context']['course_id'])
        except InvalidKeyError:
            return None

        current_unit, target_unit, subsection_id = self.get_units(json.loads(event_body['event']), record.message_type)
        data = {
            'event_type': record.message_type,
            'user_id': event_body['context']['user_id'],
            'course': course,
            'subsection_id': subsection_id,
            'current_unit': current_unit,
            'target_unit': target_unit,
            'log_time': record.log_time
        }
        self.add_cohort_id(data)
        return data if self.is_valid(data) else None

    def is_valid(self, data):
        """
        Validate a log record.
        """
        return data['user_id'] and data['current_unit'] and data['target_unit']

    def push_to_database(self, record):
        """
        Get or create StudentStepCourse.
        """
        StudentStepCourse.objects.get_or_create(**record)
