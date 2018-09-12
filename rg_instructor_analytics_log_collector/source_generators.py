import gzip
import logging

import os
from os import listdir
from os.path import isfile, join

log = logging.getLogger(__name__)

def run_ziped_file_generator(dir_name, repository):
    if not os.path.exists(dir_name) or not os.path.isdir(dir_name):
        raise Exception("Can not find log directory by nex path: {}".format(dir_name))
    processed_files = repository.get_processed_zip_files()
    for f in listdir(dir_name):
        if not f.endswith('.gz') or f in processed_files:
            continue
        with gzip.open(join(dir_name, f), 'rb') as log_file:
            logging.info('Started process next log file: {}'.format(f))
            repository.add_new_log_records(log_file.readlines())
            repository.mark_as_processed_source(f)
            logging.info('Finished process next log file: {}'.format(f))