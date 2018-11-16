"""
Processor module.
"""
from datetime import datetime
import logging
import time

from rg_instructor_analytics_log_collector.processors.course_activity_pipeline import CourseActivityPipeline
from rg_instructor_analytics_log_collector.processors.discussion_pipeline import DiscussionPipeline
from rg_instructor_analytics_log_collector.processors.enrollment_pipeline import EnrollmentPipeline
from rg_instructor_analytics_log_collector.processors.student_step_pipeline import StudentStepPipeline
from rg_instructor_analytics_log_collector.processors.video_views_pipeline import VideoViewsPipeline

log = logging.getLogger(__name__)


class Processor(object):
    """
    Processor for read raw logs and push into pipelines.
    """

    available_pipelines = [
        EnrollmentPipeline(),
        VideoViewsPipeline(),
        DiscussionPipeline(),
        StudentStepPipeline(),
        CourseActivityPipeline(),
    ]

    def __init__(self, alias_list, sleep_time):
        """
        Construct Processor.

        :param alias_list: list of the pipelines that will be loaded to the current worker.
        :param sleep_time: size of the pause between read new portion of the raw logs.
        """
        super(Processor, self).__init__()
        self.sleep_time = sleep_time
        self.pipelinies = filter(lambda x: x.alias in alias_list, self.available_pipelines)

    def run(self):
        """
        Run loop of the processor.
        """
        while True:
            for pipeline in self.pipelinies:
                logging.info('{} processor started at {}'.format(pipeline.alias, datetime.now()))
                records = pipeline.get_query()

                if not records:
                    logging.info('{} processor stopped at {} (no records)'.format(pipeline.alias, datetime.now()))
                    continue
                last_record = records.last()
                # Format raw log to the internal format.
                records = filter(None, [pipeline.format(m) for m in records])

                for record in records:
                    pipeline.push_to_database(record)

                pipeline.update_last_processed_log(last_record)
                logging.info('{} processor stopped at {}'.format(pipeline.alias, datetime.now()))

            time.sleep(self.sleep_time)
