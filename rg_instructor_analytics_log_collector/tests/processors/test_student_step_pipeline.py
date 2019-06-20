"""Test `StudentStepPipeline` functionality."""
import logging
from unittest import TestCase

from ddt import ddt, data, file_data, unpack
from mock import patch

from rg_instructor_analytics_log_collector.processors.student_step_pipeline import CourseKey
from rg_instructor_analytics_log_collector.processors.student_step_pipeline import StudentStepPipeline
from rg_instructor_analytics_log_collector.tests.processors.pipeline_test_utils import TestRecord


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
         {'event_type': TestRecord.EVENT_TYPE,
          'user_id': TestRecord.USER_ID,
          'course': "course_key",
          'subsection_id': "test_subsection_id",
          'current_unit': "test_current_unit",
          'target_unit': "test_target_unit",
          'log_time': TestRecord.LOG_TIME})
    )
    @unpack
    @patch.object(CourseKey, "from_string")
    @patch.object(StudentStepPipeline, "get_units")
    def test_format(self, units_data, test_return_value, mock_get_units, mock_course_key):
        mock_course_key.return_value = "course_key"
        mock_get_units.return_value = units_data
        self.assertEqual(self.pipeline.format(TestRecord(record_type="student_step")), test_return_value)

    def tearDown(self):
        logging.disable(logging.NOTSET)
