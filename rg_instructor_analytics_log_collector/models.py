"""
Models of the RG analytics.
"""

from django.db import models

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField


class ProcessedZipLog(models.Model):
    """
    Already processed tracking log files.
    """

    file_name = models.TextField(max_length=256)


class LogTable(models.Model):
    """
    Log Records parsed from tracking gzipped log file.
    """

    message_type_hash = models.CharField(max_length=255, db_index=True)
    message_type = models.TextField()
    log_time = models.DateTimeField(db_index=True)
    user_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    log_message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:  # NOQA
        unique_together = ('message_type_hash', 'log_time', 'user_name')
        ordering = ['-log_time']

    def __unicode__(self):  # NOQA
        return u'{} {}'.format(self.message_type, self.log_time)


class EnrollmentByDay(models.Model):
    """
    Cumulative per-day Enrollment stats.
    """

    day = models.DateField(db_index=True)
    total = models.IntegerField(default=0)
    enrolled = models.IntegerField(default=0)
    unenrolled = models.IntegerField(default=0)
    course = CourseKeyField(max_length=255, db_index=True)
    last_updated = models.DateField(auto_now=True, null=True)

    class Meta:  # NOQA
        unique_together = ('course', 'day',)
        ordering = ['-day']

    def __unicode__(self):  # NOQA
        return u'{} {}'.format(self.day, self.course)


class LastProcessedLog(models.Model):
    """
    Last processed LogTable by Processor.
    """

    ENROLLMENT = 'EN'
    VIDEO_VIEWS = 'VI'

    PROCESSOR_CHOICES = (
        (ENROLLMENT, 'Enrollment'),
        (VIDEO_VIEWS, 'VideoViews'),
    )

    log_table = models.ForeignKey(LogTable)
    processor = models.CharField(max_length=2, choices=PROCESSOR_CHOICES, unique=True)
