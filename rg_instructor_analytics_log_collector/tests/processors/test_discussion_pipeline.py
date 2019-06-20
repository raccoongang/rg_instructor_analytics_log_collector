"""
Test discussion pipeline logic.
"""
import logging
from unittest import skip, TestCase

from ddt import ddt, data, file_data, unpack
from mock import patch

from rg_instructor_analytics_log_collector.processors.discussion_pipeline import CourseKey
from rg_instructor_analytics_log_collector.processors.discussion_pipeline import DiscussionPipeline
from rg_instructor_analytics_log_collector.tests.processors.pipeline_test_utils import TestRecord


@ddt
class TestDiscussionPipeline(TestCase):
    """
    Test `DiscussionPipeline` logic.
    """

    def setUp(self):
        logging.disable(logging.DEBUG)
        self.pipeline = DiscussionPipeline()

    @file_data("test_resources/test_discussion_pipeline_records.json")
    @unpack
    def test_is_valid(self, entry):
        self.assertEqual(self.pipeline.is_valid(entry.get("data")), entry.get("is_valid"))

    @skip("Skip till `TestRecord` is made pipeline-dependent")
    def test_format(self):
        pass
