"""
Test the `Processor` module.
"""
import logging
from unittest import TestCase

from ddt import ddt, data, unpack
from mock import patch

from rg_instructor_analytics_log_collector.processors.processor import Processor
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline
from rg_instructor_analytics_log_collector.processors.student_step_pipeline import StudentStepPipeline


class TestRecords(object):
    """
    Dummy iterator class.
    """

    def __iter__(self):
        """
        Allow for iterating over test records.

        Returns:
            iterator object to iterate over test records.
        """
        return iter([1, 2, 3])  # TODO make it dynamically defined (and update tests respectively)

    @staticmethod
    def exists():
        """
        Allows for overriding a namesake method.
        """
        return True


@ddt
class TestProcessor(TestCase):

    def setUp(self):
        logging.disable(logging.DEBUG)
        # Doesn't matter which one to pick
        Processor.available_pipelines = [StudentStepPipeline()]
        self.processor = Processor(alias_list=["student_step"], sleep_time=1)

    @data(({"test_key": "test_value"}, 3),
          (None, 0))
    @unpack
    @patch.object(BasePipeline, "get_query")
    @patch.object(StudentStepPipeline, "get_units")
    @patch.object(StudentStepPipeline, "format")
    @patch.object(StudentStepPipeline, "push_to_database")
    @patch.object(StudentStepPipeline, "update_last_processed_log")
    def test_process_push_to_database(
            self,
            format_data,
            times_called,
            mock_update_last_processed_log,
            mock_push_to_database,
            mock_format,
            mock_get_units,
            mock_get_query
            ):
        """
        Ensure only significant data is pushed to a db.
        """
        mock_update_last_processed_log.return_value = None
        mock_push_to_database.return_value = None
        mock_get_units.return_value = (None, None, None)
        mock_get_query.return_value = TestRecords()

        mock_format.return_value = format_data

        self.processor.process()
        # TODO Also, ensure it's called as many times as there are records in the pipeline
        self.assertEqual(mock_push_to_database.call_count, times_called)

    # TODO implement
    def test_process_exception(self):
        """
        Ensure the flow doesn't stop if any error occurs.
        """

    def tearDown(self):
        logging.disable(logging.NOTSET)
