"""
Processor module.
"""
from datetime import datetime
import logging
import time

from rg_instructor_analytics_log_collector.models import LastProcessedLog, LogTable
from rg_instructor_analytics_log_collector.processors.base_pipeline import EnrollmentPipeline
from django.db.models import Min, Max
from django.db import transaction

log = logging.getLogger(__name__)


class Processor(object):
    """
    Processor for read raw logs and push into pipelines.
    """

    available_pipelines = [
        EnrollmentPipeline()
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

    def _get_query_for_pipeline(self, pipeline):
        """
        Return list of the raw logs wit type, that suitable for the given pipeline.
        """
        query = LogTable.objects.filter(message_type__in=pipeline.supported_types)
        last_processed_log_date = pipeline.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(log_time__gt=last_processed_log_date)

        return query.order_by('log_time')

    def delete_logs(self):
        """Delete all unused log records."""
        last_date = LastProcessedLog.get_last_date()

        if last_date:
            records = LogTable.objects.filter(log_time__lt=last_date).order_by('log_time')
            chunk_size = self.CHUNK_SIZE_DELETE

            while records.exists():
                if records.count() > chunk_size:
                    delete_max_time = records[chunk_size].log_time
                else:
                    delete_max_time = last_date

                logging.info('Deleting log records older than {}'.format(delete_max_time))

                with transaction.atomic():
                    LogTable.objects.filter(log_time__lt=delete_max_time).delete()

                records = LogTable.objects.filter(log_time__lt=last_date).order_by('log_time')

    def run(self, delete_logs=False):
        """
        Run loop of the processor.
        """
        while True:
            for pipeline in self.pipelinies:
                records = self._get_query_for_pipeline(pipeline)
                last_record = records.last()

                if not records.exists():
                    logging.debug('{} processor stopped at {} (no records)'.format(pipeline.alias, datetime.now()))
                    continue

                time_start = datetime.now()
                logging.info('{} processor started at {}'.format(pipeline.alias, time_start))

                chunk_size = self.CHUNK_SIZE_PROCESSOR
                records_counter = 0
                records_pushed_counter = 0
                records_count = records.count()

                for offset in range(0, records_count, chunk_size):

                    logging.info('{}: total records: {}. processing from {} to {}'.format(
                                pipeline.alias,records_count,offset,offset+chunk_size))

                    for record in records[offset:offset+chunk_size]:
                        data_record = pipeline.format(record)
                        records_counter += 1

                        if data_record:
                            pipeline.push_to_database(data_record)
                            records_pushed_counter += 1
                        pipeline.update_last_processed_log(record)

                logging.info(
                    '{} processor stopped at {} (processed: {}, saved: {}, rate: {} rps)'.format(
                        pipeline.alias, datetime.now(), records_counter, records_pushed_counter,
                        int(records_counter / (datetime.now() - time_start).total_seconds())
                    )
                )

            if delete_logs:
                self.delete_logs()

            time.sleep(self.sleep_time)
