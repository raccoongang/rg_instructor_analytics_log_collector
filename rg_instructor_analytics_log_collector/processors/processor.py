"""
Processor module.
"""
import logging
import operator
import time
from datetime import datetime

from rg_instructor_analytics_log_collector.processors.enrollment_pipeline import EnrollmentPipeline
from rg_instructor_analytics_log_collector.processors.discussion_pipeline import DiscussionPipeline
from rg_instructor_analytics_log_collector.processors.video_views_pipeline import VideoViewsPipeline

log = logging.getLogger(__name__)


class Processor(object):
    """
    Processor for read raw logs and push into pipelines.
    """

    available_pipelines = [
        EnrollmentPipeline(),
        VideoViewsPipeline(),
        DiscussionPipeline()
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

    def _sort(self, ordering, records):
        """
        Sort list of the records with given order list.

        :param ordering: list where each record - name of the field for sort.
        For reverse sort add to the start of the field `-` character.

        :param records: list of the unsorted records.
        """
        for order in ordering:
            reverse = False
            if order.startswith('-'):
                reverse = True
                order = order[1:]
            records.sort(reverse=reverse, key=operator.itemgetter(order))
        return records

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
                records = self._sort(pipeline.ordered_fields, records)
                if pipeline.alias == EnrollmentPipeline.alias:
                    records = pipeline.aggregate(records)

                for record in records:
                    db_context = pipeline.load_database_contex(record)
                    pipeline.push_to_database(record, db_context)

                pipeline.update_last_processed_log(last_record)
                logging.info('{} processor stopped at {}'.format(pipeline.alias, datetime.now()))

            time.sleep(self.sleep_time)
