"""
Test `StudentStepPipeline` functionality.
"""
from mock import patch
from unittest import TestCase

from rg_instructor_analytics_log_collector.processors.processor import Processor
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline
from rg_instructor_analytics_log_collector.processors.student_step_pipeline import StudentStepPipeline


# TODO disable logging
class TestStudentStepPipeline(TestCase):
    """
    Test `StudentStepPipeline` logic.
    """

    # TODO test `is_valid` (ddt)
    # TODO test `format`;
    #  mock `get_units()`
    #  caution (to double check): `course = CourseKey.from_string(event_body['context']['course_id'])`
