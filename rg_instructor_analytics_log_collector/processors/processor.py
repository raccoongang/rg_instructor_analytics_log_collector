"""
Processor module.
"""
from datetime import datetime
import logging
import time

from rg_instructor_analytics_log_collector.models import LogTable
from rg_instructor_analytics_log_collector.processors.base_pipeline import EnrollmentPipeline

log = logging.getLogger(__name__)


class Processor(object):
    """
    Processor for read raw logs and push into pipelines.
    """

    available_pipelines = [
        EnrollmentPipeline()
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

    def _get_query_for_pipeline(self, pipeline):
        """
        Return list of the raw logs wit type, that suitable for the given pipeline.
        """
        query = LogTable.objects.filter(message_type__in=pipeline.supported_types)
        last_processed_log_date = pipeline.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(created__gt=last_processed_log_date)

        return query.order_by('created')

    def run(self):
        """
        Run loop of the processor.
        """
        while True:
            for pipeline in self.pipelinies:
                logging.info('{} processor started at {}'.format(pipeline.alias, datetime.now()))
                records = self._get_query_for_pipeline(pipeline)
                last_record = records.last()

                if not records:
                    logging.info('{} processor stopped at {} (no records)'.format(pipeline.alias, datetime.now()))
                    continue

                records = filter(None, [pipeline.format(record) for record in records])

                for record in records:
                    pipeline.push_to_database(record)

                pipeline.update_last_processed_log(last_record)
                logging.info('{} processor stopped at {}'.format(pipeline.alias, datetime.now()))
            time.sleep(self.sleep_time)
