"""
Module with processor.
"""
import logging
import operator
import time


from django.db.models import Q


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
        type_request = None
        for pipeline_type in pipeline.supported_types:
            if type_request is None:
                type_request = Q(message_type__contains=pipeline_type)
            else:
                type_request |= Q(message_type__contains=pipeline_type)

        query = LogTable.objects.filter(type_request)
        last_date = pipeline.retrieve_last_date()
        if last_date:
            query &= LogTable.objects.filter(log_time__lt=last_date)
        return query.order_by('log_time').all()

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
                records = self._get_query_for_pipeline(pipeline)
                if not records:
                    continue
                if pipeline.format:
                    records = filter(None, [pipeline.format(m) for m in records])
                if pipeline.ordered_fields:
                    records = self._sort(pipeline.ordered_fields(), records)
                if pipeline.aggregate:
                    records = pipeline.aggregate(records)
                for m in records:
                    db_context = pipeline.load_database_contex and pipeline.load_database_contex(m) or None
                    pipeline.push_to_database(m, db_context)
            time.sleep(self.sleep_time)
