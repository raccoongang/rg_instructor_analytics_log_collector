"""
Processor module.
"""
import logging
import operator
import time
from datetime import datetime

from django.db.models import Q

from rg_instructor_analytics_log_collector.models import LogTable
from rg_instructor_analytics_log_collector.processors.base_pipeline import EnrollmentPipeline
from rg_instructor_analytics_log_collector.processors.discussion_pipeline import DiscussionPipeline

log = logging.getLogger(__name__)


class Processor(object):
    """
    Processor for read raw logs and push into pipelines.
    """

    available_pipelines = [
        EnrollmentPipeline(),
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

    def _get_query_for_pipeline(self, pipeline):
        """
        Return list of the raw logs wit type, that suitable for the given pipeline.
        """
        type_request = None
        for pipeline_type in pipeline.supported_types:
            if type_request is None:
                type_request = Q(message_type__contains=pipeline_type)
            else:
                type_request |= Q(message_type__contains=pipeline_type)

        query = LogTable.objects.filter(type_request)
        last_processed_log_date = pipeline.retrieve_last_date()
        if last_processed_log_date:
            query = query.filter(created__gte=last_processed_log_date)
        return query.order_by('log_time')

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
                records = self._get_query_for_pipeline(pipeline)

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
