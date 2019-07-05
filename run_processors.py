"""
Entrypoint.
"""

import argparse

import django
django.setup()

from rg_instructor_analytics_log_collector.processors.processor import Processor


def main():
    """
    Start app.
    """
    parser = argparse.ArgumentParser(description='App for load logs records in to mysql')
    parser.add_argument('-a', '--aliases', nargs='+', type=list, help='List of the aliases', required=True)
    parser.add_argument(
        '--sleep_time',
        action="store",
        dest="sleep_time",
        help="Time between refreshing statistic(in seconds)",
        type=int,
        default=300
    )
    parser.add_argument('--delete-logs', action="store_true", help='Delete all unused log records from database')
    arg = parser.parse_args()
    # aliases represent as list of the car lists. We need convert it to the list of the strings.
    alias_list = [str(''.join(a)) for a in arg.aliases]

    processor = Processor(alias_list, arg.sleep_time)
    processor.run(delete_logs=arg.delete_logs)


if __name__ == "__main__":
    main()
