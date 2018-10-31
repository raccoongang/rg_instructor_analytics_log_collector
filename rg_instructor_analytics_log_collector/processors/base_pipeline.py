"""
Collection of the base pipelines.
"""

from abc import ABCMeta, abstractmethod


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

    @abstractmethod
    def retrieve_last_date(self):
        """
        Return date of the last processed record (or None for the first run).
        """
        pass

    @abstractmethod
    def get_query(self):
        """
        Return list of the raw logs with type, that suitable for the given pipeline.
        """
        pass

    def format(self, record):
        """
        Process raw message with different format to the single format.

        Note, if there no needs to change format set it as property, that equal to None.

        In case, when given record dosent relate to the given pipeline - return None.
        :param record:  raw log record.
        :return: dictionary with consistent structure.
        """
        return None

    @property
    def ordered_fields(self):
        """
        Return list of the filed for sort.

        If needed reverse sorting - use symbol `-` before field name.
        """
        return []

    def aggregate(self, records):
        """
        Return generator with sutable agregated structure.

        I.E. records can be grouped by course and day.

        If function return None - the no aggregation needed.
        """
        return None

    def load_database_contex(self, aggregated_records):
        """
        Return context, needed for final processing.

        In this method pipeline must call databse for additional information.
        """
        return None

    def push_to_database(self, aggregated_records, db_context):
        """
        Push to db final result.
        """
