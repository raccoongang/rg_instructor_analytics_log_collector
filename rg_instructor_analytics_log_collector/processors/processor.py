"""
Module with processor.
"""
from importlib import import_module
import inspect
import logging
import operator
from os import listdir
from os.path import isfile, join
import time


from django.db.models import Q
from twisted.python.reflect import ModuleNotFound


from rg_instructor_analytics_log_collector.models import LogTable
from rg_instructor_analytics_log_collector.processors.base_pipeline import BasePipeline


log = logging.getLogger(__name__)


class Processor(object):
    """
    Processor for read raw logs and push into pipelines.
    """

    def __init__(self, alias_list, sleep_time):
        """
        Construct Processor.

        :param alias_list: list of the pipelines that will be loaded to the current worker.
        :param sleep_time: size of the pause between read new portion of the raw logs.
        """
        super(Processor, self).__init__()
        self.sleep_time = sleep_time
        self.pipelinies = self.load_all_pipeline(alias_list)

    def load_all_pipeline(self, alias_list):
        """
        Load pipelines from the rg_instructor_analytics_log_collector.processors.

        All pipelines must be places inside the rg_instructor_analytics_log_collector.processors package
        :param alias_list: list of piplines that must be loaded. Rest will be ignored.
        """
        pipeline_classes = set()
        root_package = 'rg_instructor_analytics_log_collector.processors'
        try:
            snippets_pkg = import_module(root_package)
            package_path = snippets_pkg.__path__[0]
            files = [
                f.replace('.py', '') for f in listdir(package_path) if
                isfile(join(package_path, f)) and f.endswith('.py')
            ]
            for file in files:
                module = import_module(root_package + '.' + file)
                members = inspect.getmembers(module)
                for name, body in members:
                    if not callable(body):
                        continue
                    if body.__name__ == BasePipeline.__name__:
                        continue
                    try:
                        if issubclass(body, BasePipeline):
                            pipeline_classes.add(body)
                    except TypeError as e:
                        log.debug("Can not check type in the loading pipeline, {}".format(repr(e)))
        except ModuleNotFound as e:
            log.error('can not load pipelines {}'.format(repr(e)))

        if len(pipeline_classes) == 0:
            raise Exception("There no Pipline classes, please check you settings and environments")
        return filter(lambda x: x.alias() in alias_list, [pipeline() for pipeline in pipeline_classes])

    def _get_query_for_pipeline(self, pipeline):
        """
        Return list of the raw logs wit type, that suitable for the given pipeline.
        """
        type_request = None
        for pipeline_type in pipeline.supported_types():
            if type_request is None:
                type_request = Q(message_type__contains=pipeline_type)
            else:
                type_request |= Q(message_type__contains=pipeline_type)
        if type_request is None:
            return None

        query = LogTable.objects.filter(type_request)
        last_date = pipeline.last_date()
        if last_date:
            query &= LogTable.objects.filter(log_time__lt=pipeline.last_date())
        return query.order_by('log_time').all()

    def _sort(self, ordering, messages):
        """
        Sort list of the records with given order list.

        :param ordering: list where each record - name of the field for sort.
        For reverse sort add to the start of the field `-` character.

        :param messages: list of the unsorted messages.
        """
        for order in ordering:
            reverse = False
            if order.startswith('-'):
                reverse = True
                order = order[1:]
            messages.sort(reverse=reverse, key=operator.itemgetter(order))
        return messages

    def run(self):
        """
        Run loop of the processor.
        """
        while True:
            for pipeline in self.pipelinies:
                messages = self._get_query_for_pipeline(pipeline)
                if not messages:
                    continue
                if pipeline.format:
                    messages = filter(None, [pipeline.format(m) for m in messages])
                if pipeline.ordered_fields:
                    messages = self._sort(pipeline.ordered_fields(), messages)
                if pipeline.aggregate:
                    messages = pipeline.aggregate(messages)
                for m in messages:
                    db_context = pipeline.load_database_contex and pipeline.load_database_contex(m) or None
                    pipeline.push_to_database(m, db_context)
            time.sleep(self.sleep_time)
