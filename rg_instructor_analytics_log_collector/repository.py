"""
Module for the provide general access to the storage for the logs (i.e. mySql).
"""
from abc import ABCMeta, abstractmethod
import json
import logging

from rg_instructor_analytics_log_collector.models import LogTable, ProcessedZipLog

log = logging.getLogger(__name__)


class IRepository(object):
    """
    Base repository class.
    """

    __metaclass__ = ABCMeta

    def _get_logs_batch_size(self):
        """
        Provide batch size for the bulk operation.
        """
        return 1024

    @abstractmethod
    def get_processed_zip_files(self):
        """
        Return list of the files, that already processed.
        """
        pass

    def add_new_log_records(self, log_strings_list):
        """
        Parse the list of raw string into records inside a database.
        """
        log_buf = []
        for log_string in log_strings_list:
            try:
                json_log = json.loads(log_string)
                log_buf.append({
                    'message_type': 'event_type' in json_log and json_log['event_type'] or json_log['name'],
                    'log_time': 'time' in json_log and json_log['time'] or json_log['timestamp'],
                    'log_message': log_string,
                    'user_name': json_log.get('username', json_log.get('context', {}).get('username'))
                })
            except ValueError as e:
                log.error('can not parse json from the log string ({})\n\t{}'.format(log_string, repr(e)))
                return
            except (IndexError, KeyError) as e:
                log.exception('corrupted structure of the log json ({})\n\t{}'.format(log_string, repr(e)))
            if len(log_buf) >= self._get_logs_batch_size():
                self.store_new_log_message(log_buf)
                log_buf = []

        self.store_new_log_message(log_buf)

    @abstractmethod
    def store_new_log_message(self, parsed_logs_list):
        """
        Store list of the parsed log record into the database.
        """
        pass

    @abstractmethod
    def mark_as_processed_source(self, source_name):
        """
        Mark zip file as processed.
        """
        pass


class MySQlRepository(IRepository):
    """
    Implementation of the repository for the mySql.
    """

    def get_processed_zip_files(self):
        """
        Return list of the file names, that already was processed.
        """
        return ProcessedZipLog.objects.values_list('file_name', flat=True)

    def store_new_log_message(self, parsed_logs_list):
        """
        Store parsed logs into the database.
        """
        LogTable.objects.bulk_insert_or_update(
            create_fields=['message_type', 'log_time', 'user_name', 'log_message'],
            update_fields=['log_message'],
            values=[[
                log_dict['message_type'],
                log_dict['log_time'],
                log_dict['user_name'],
                log_dict['log_message'],
            ] for log_dict in parsed_logs_list]
        )

    def mark_as_processed_source(self, source_name):
        """
        Mark given file name as processed.
        """
        ProcessedZipLog.objects.create(file_name=source_name)
