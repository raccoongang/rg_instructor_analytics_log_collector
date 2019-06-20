"""
Test `StudentStepPipeline` functionality.
"""
import logging
import json
from unittest import TestCase

from ddt import ddt, data, file_data, unpack
from mock import patch

from rg_instructor_analytics_log_collector.processors.student_step_pipeline import StudentStepPipeline
from rg_instructor_analytics_log_collector.processors.student_step_pipeline import CourseKey


class TestRecord(object):
    """
    Dummy record class.
    """
    log_time = 123
    user_id = 123
    event_type = "test_event_type"
    course_id = 456

    def __init__(self):
        self.log_message = json.dumps({"event": json.dumps({"test_key": "test_value"}),
                                      "context": {"user_id": self.user_id,
                                                  "course_id": self.course_id}})
        self.message_type = self.event_type

    def log_message(self):
        return self.log_message


@ddt
class TestStudentStepPipeline(TestCase):
    """
    Test `StudentStepPipeline` logic.
    """

    def setUp(self):
        logging.disable(logging.DEBUG)
        self.pipeline = StudentStepPipeline()

    @file_data("test_resources/test_student_step_pipeline_records.json")
    @unpack
    def test_is_valid(self, entry):
        self.assertEqual(self.pipeline.is_valid(entry.get("data")), entry.get("is_valid"))

    @data(
        ((None, None, None), None),
        (("test_current_unit", None, None), None),
        (("test_current_unit", "test_target_unit", None), None),
        (("test_current_unit", "test_target_unit", "test_subsection_id"),
         {'event_type': TestRecord.event_type,
          'user_id': TestRecord.user_id,
          'course': "course_key",
          'subsection_id': "test_subsection_id",
          'current_unit': "test_current_unit",
          'target_unit': "test_target_unit",
          'log_time': TestRecord.log_time})
    )
    @unpack
    @patch.object(CourseKey, "from_string")
    @patch.object(StudentStepPipeline, "get_units")
    def test_format(self, units_data, test_return_value, mock_get_units, mock_course_key):
        mock_course_key.return_value = "course_key"
        mock_get_units.return_value = units_data
        self.assertEqual(self.pipeline.format(TestRecord()), test_return_value)

    def tearDown(self):
        logging.disable(logging.NOTSET)
