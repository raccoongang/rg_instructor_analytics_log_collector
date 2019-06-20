"""
Test `CourseActivityPipeline` functionality.
"""
import logging
from unittest import skip, TestCase

from ddt import ddt, data, file_data, unpack
from mock import patch

from rg_instructor_analytics_log_collector.processors.course_activity_pipeline import CourseActivityPipeline
from rg_instructor_analytics_log_collector.processors.course_activity_pipeline import CourseKey
from rg_instructor_analytics_log_collector.tests.processors.pipeline_test_utils import TestRecord


@ddt
class TestCourseActivityPipeline(TestCase):
    """
    Test `CourseActivityPipeline` logic.
    """

    def setUp(self):
        logging.disable(logging.DEBUG)
        self.pipeline = CourseActivityPipeline()

    @file_data("test_resources/test_course_activity_pipeline_records.json")
    @unpack
    def test_is_valid(self, entry):
        self.assertEqual(self.pipeline.is_valid(entry.get("data")), entry.get("is_valid"))

    @data(
        (None, None, None),
        ("test_course_id", None, None),
        (None, "test_user_id", None),
        ("test_course_id", "test_user_id",
         {'user_id': "test_user_id",
          'course_id': "test_course_id",
          'log_time': TestRecord.LOG_TIME})
    )
    @unpack
    @patch.object(CourseKey, "from_string")
    def test_format(self, course_id, user_id, test_return_value, mock_course_key):
        mock_course_key.return_value = "course_key"
        self.assertEqual(self.pipeline.format(TestRecord(user_id=user_id,
                                                         course_id=course_id)),
                         test_return_value)

    def tearDown(self):
        logging.disable(logging.NOTSET)
