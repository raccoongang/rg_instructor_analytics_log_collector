https://travis-ci.org/raccoongang/rg_instructor_analytics_log_collector.svg?branch=master

# rg_instructor_analytics_log_collector [Not Supported]

This repository is archived and not supported.

RaccoonGang decided to continue developing analytics service on private basis
the current available product version is 3.x.x. 

Please find more information on our site 
[RG Instructor Analytics](https://raccoongang.com/case-studies/rg-analytics-open-edx/)

## Util for the tracking log parsing and storing it into mySql databse 

## Setup 
* Install requirements
* Set next environment variables: DJANGO_SETTINGS_MODULE and SERVICE_VARIANT
    * Example:
    >DJANGO_SETTINGS_MODULE = lms.envs.devstack
    SERVICE_VARIANT = lms
* Add to the django installed app 
* Install package in to the environment with edx-platform
* Run migrations

## Run
```bash
python main.py [--tracking_log_dir]
```
argument tracking_log_dir point to the log directory, by default it equal tp `/edx/var/log/tracking`
