"""
Enterpoint.
"""
import argparse
import time

import django
django.setup()

from rg_instructor_analytics_log_collector.raw_log_loaders import run_ziped_file_loader
from rg_instructor_analytics_log_collector.repository import MySQlRepository


def main():
    """
    Start app.
    """
    parser = argparse.ArgumentParser(
        description='App for load logs records in to mysql'
    )
    parser.add_argument(
        '--tracking_log_dir',
        action="store",
        dest="tracking_log_dir",
        type=str,
        default='/edx/var/log/tracking'
    )
    parser.add_argument(
        '--sleep_time',
        action="store",
        dest="sleep_time",
        help="Time between refreshing statistic(in seconds)",
        type=int,
        default=300
    )
    parser.add_argument('--reload-logs', action="store_true", help='Reload all logs from files into database')

    arg = parser.parse_args()
    django.setup()

    while True:
        repository = MySQlRepository()
        run_ziped_file_loader(arg.tracking_log_dir, repository, reload_logs=arg.reload_logs)
        time.sleep(arg.sleep_time)


if __name__ == "__main__":
    main()
