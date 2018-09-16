https://travis-ci.org/raccoongang/rg_instructor_analytics_log_collector.svg?branch=master
# Util for the tracking log parsing and storing it into mySql databse 

## Setup 
* Install requirements
* Set next environment variables: DJANGO_SETTINGS_MODULE and SERVICE_VARIANT
    * Example:
    >DJANGO_SETTINGS_MODULE = lms.envs.devstack
    SERVICE_VARIANT = lms
* Add to the django installed app 
* Install package in to the environment with edx-platform
* Run migrations
* Ensure, that app has access to the log directory

## Run Log Watcher
```bash
python run_log_watcher.py [--tracking_log_dir] [--sleep_time]
```
* argument tracking_log_dir point to the log directory, by default it equal tp `/edx/var/log/tracking`
* argument sleep_time count seconds before rescan the log direcotry. Default - 5 minutes.

## Run Processors
```bash
python run_processors.py [--aliases] [--sleep_time]
```
* aliases - list of the aliases for run. I.E. `enrollment` 
* argument sleep_time count seconds before rescan the log direcotry. Default - 5 minutes.
