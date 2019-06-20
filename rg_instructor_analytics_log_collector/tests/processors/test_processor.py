"""
Test the `Processor` module.
"""
from mock import patch
from unittest import TestCase

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
        return iter([1, 2, 3])

    @staticmethod
    def exists():
        """
        Allows for overriding a namesake method.
        """
        return True

    # TODO add `record.log_message`


# TODO disable logging
class TestProcessor(TestCase):

    def setUp(self):
        # Doesn't matter which one to pick
        Processor.available_pipelines = [StudentStepPipeline()]
        self.processor = Processor(alias_list=["student_step"], sleep_time=1)

    # TODO consider using `ddt` whenever possible
    # TODO refactor the original code for the sake of fewer mocks
    # TODO patch differently
    @patch.object(BasePipeline, "get_query", return_value=TestRecords())  # TODO consider mocking queryset
    @patch.object(StudentStepPipeline, "get_units", return_value=(None, None, None))
    @patch.object(StudentStepPipeline, "format", return_value=None)
    @patch.object(StudentStepPipeline, "push_to_database", return_value=None)
    @patch.object(StudentStepPipeline, "update_last_processed_log", return_value=None)
    def test_empty_records_data(
            self,
            mock_update_last_processed_log,
            mock_push_to_database,
            mock_format,
            mock_get_units,
            mock_get_query
            ):
        """
        Ensure no empty data is pushed to a db.
        """
        self.processor.process()
        mock_push_to_database.assert_not_called()

    # TODO test Exception raising to ensure the flow doesn't stop if any error occurs
