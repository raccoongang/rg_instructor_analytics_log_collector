"""
Processor module.
"""
from datetime import datetime
import logging
import time

from rg_instructor_analytics_log_collector.models import LastProcessedLog, LogTable
from rg_instructor_analytics_log_collector.processors.course_activity_pipeline import CourseActivityPipeline
from rg_instructor_analytics_log_collector.processors.discussion_pipeline import DiscussionPipeline
from rg_instructor_analytics_log_collector.processors.enrollment_pipeline import EnrollmentPipeline
from rg_instructor_analytics_log_collector.processors.student_step_pipeline import StudentStepPipeline
from rg_instructor_analytics_log_collector.processors.video_views_pipeline import VideoViewsPipeline
from django.db.models import Min, Max
from django.db import transaction

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

    CHUNK_SIZE_PROCESSOR = 10000
    CHUNK_SIZE_DELETE = 50000

    def __init__(self, alias_list, sleep_time):
        """
        Construct Processor.

        :param alias_list: list of the pipelines that will be loaded to the current worker.
        :param sleep_time: size of the pause between read new portion of the raw logs.
        """
        super(Processor, self).__init__()
        self.sleep_time = sleep_time
        self.pipelinies = filter(lambda x: x.alias in alias_list, self.available_pipelines)

    def process(self):
        """
        Process records data.

        Fetch data records from pipelines and
        store them in a database.
        """
        for pipeline in self.pipelinies:
            records = pipeline.get_query()

            if not records.exists():
                logging.debug('{} processor stopped at {} (no records)'.format(pipeline.alias, datetime.now()))
                continue

            logging.info('{} processor started at {}'.format(pipeline.alias, datetime.now()))

            chunk_size = self.CHUNK_SIZE_PROCESSOR
            records_counter = 0
            records_pushed_counter = 0

            records_count = records.count()
            offset = 0
            while offset < records_count:
                limit = chunk_size
                if offset + limit > records_count:
                    limit = records_count - offset

                logging.debug('{}: total records: {}. processing from {} to {} limit {}'.format(
                             pipeline.alias,records_count,offset,offset+limit,limit))

                for record in records[offset:offset+limit]:
                    # Format raw log to the internal format.
                    data_record = pipeline.format(record)
                    records_counter += 1

                    if data_record:
                        pipeline.push_to_database(data_record)
                        records_pushed_counter += 1
                    pipeline.update_last_processed_log(record)

                offset += limit

            logging.info(
                '{} processor stopped at {} (processed: {}, saved: {})'.format(
                pipeline.alias, datetime.now(), records_counter, records_pushed_counter))

    def delete_logs(self):
        """Delete all unused log records."""
        last_date = LastProcessedLog.get_last_date()

        if last_date:
            chunk_size = self.CHUNK_SIZE_DELETE

            records_ids =  LogTable.objects.filter(log_time__lt=last_date).aggregate(Min('id'), Max('id'))
            records_min_id = records_ids['id__min']
            records_max_id = records_ids['id__max']

            while records_min_id and records_max_id and records_min_id <= records_max_id:
                delete_max_id = records_min_id + chunk_size
                if delete_max_id > records_max_id:
                    delete_max_id = records_max_id

                logging.debug('deleting old log records. from id {} to id {}'.format(records_min_id, delete_max_id))

                with transaction.atomic():
                    LogTable.objects.filter(id__lte=delete_max_id, id__gte=records_min_id).delete()

                records_min_id += chunk_size

    def run(self, delete_logs=False):
        """Run loop of the processor."""
        while True:
            self.process()
            if delete_logs:
                self.delete_logs()
            time.sleep(self.sleep_time)
