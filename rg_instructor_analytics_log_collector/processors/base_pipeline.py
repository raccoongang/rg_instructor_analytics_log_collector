"""
Collection of the base pipelines.
"""

from abc import ABCMeta, abstractmethod

from rg_instructor_analytics_log_collector.models import LastProcessedLog, LogTable


class BasePipeline(object):
    """
    Base Pipeline.

    NOTE: After implementing new pipeline, add it to the Processor.
    """

    __metaclass__ = ABCMeta

    """
    Readable name of the pipeline.
    """
    alias = None

    """
    Supported log types list.
    See:
    https://edx.readthedocs.io/projects/devdata/en/stable/internal_data_formats/event_list.html#event-list
    """
    supported_types = None
    """
    Processor name for the last processed LogTable.
    """
    processor_name = None

    def retrieve_last_date(self):
        """
        Fetch the moment of time daily enrollments were lastly updated.

        :return: DateTime or None
        """
        last_processed_log_table = LastProcessedLog.objects.filter(
            processor=self.processor_name
        ).first()

        return last_processed_log_table and last_processed_log_table.log_table.created

    def get_query(self):
        """
        Return list of the raw logs with type, that suitable for the given pipeline.
        """
        query = LogTable.objects.filter(message_type__in=self.supported_types)
        last_processed_log_date = self.retrieve_last_date()

        if last_processed_log_date:
            query = query.filter(created__gt=last_processed_log_date)

        return query.order_by('created')

    @abstractmethod
    def format(self, record):
        """
        Process raw message with different format to the single format.

        Note, if there no needs to change format set it as property, that equal to None.

        In case, when given record dosent relate to the given pipeline - return None.
        :param record:  raw log record.
        :return: dictionary with consistent structure.
        """
        pass

    @abstractmethod
    def push_to_database(self, formatted_record):
        """
        Push to db final result.
        """
        pass

    def update_last_processed_log(self, last_record):
        """
        Create or update last processed LogTable by Processor.
        """
        if last_record:
            LastProcessedLog.objects.update_or_create(processor=self.processor_name,
                                                      defaults={'log_table': last_record})
