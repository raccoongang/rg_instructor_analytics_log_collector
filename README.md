https://travis-ci.org/raccoongang/rg_instructor_analytics_log_collector.svg?branch=master

# Util for the tracking log parsing and storing it into mySql databse 

> Relies on [Edx Event Tracking](https://github.com/edx/event-tracking) system's `logger` backend
> - https://event-tracking.readthedocs.io/en/latest/

## Glossary

Event (Edx Event)
> context-aware semi-structured data items with nested data structures;

Tracker
>

Processor
>

Pipeline
>

Record
>

## Setup

* Install requirements
* Set next environment variables: DJANGO_SETTINGS_MODULE and SERVICE_VARIANT
```
# Example:
DJANGO_SETTINGS_MODULE = lms.envs.devstack
SERVICE_VARIANT = lms
```
* Add to the django installed app
* Install package in to the environment with edx-platform
* Run migrations
* Ensure app has an access to the log directory

## Log Watcher running

```
# bash
python run_log_watcher.py [--tracking_log_dir] [--sleep_time]
```
- `tracking_log_dir` points to the log directory (default: `/edx/var/log/tracking`)
- `sleep_time` - log directory rescan period (seconds, default: 5 minutes).

## Run Processors
If you install the Analytics at the first time, run `Processors` after `Log Watcher` running has finished.

```
# bash
python run_processors.py [--aliases] [--sleep_time]
```
- `aliases` - aliases list to run (i.e. `enrollment`)
- `sleep_time` - log directory rescan period (seconds, default: 5 minutes).
