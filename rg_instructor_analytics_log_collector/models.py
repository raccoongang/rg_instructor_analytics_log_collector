"""
Models of the RG analytics.
"""
from django.core.validators import validate_comma_separated_integer_list
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

    message_type = models.CharField(max_length=255, db_index=True)
    log_time = models.DateTimeField(db_index=True)
    user_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    log_message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:  # NOQA
        unique_together = ('message_type', 'log_time', 'user_name')
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
    DISCUSSION_ACTIVITY = 'DA'

    PROCESSOR_CHOICES = (
        (ENROLLMENT, 'Enrollment'),
        (VIDEO_VIEWS, 'VideoViews'),
        (DISCUSSION_ACTIVITY, 'Discussion activity'),
    )

    log_table = models.ForeignKey(LogTable)
    processor = models.CharField(max_length=2, choices=PROCESSOR_CHOICES, unique=True)


class VideoViewsByUser(models.Model):
    """
    User's Video Views info.
    """

    course = CourseKeyField(max_length=255, db_index=True)
    user_id = models.IntegerField(db_index=True)
    video_block_id = models.CharField(max_length=255, db_index=True)
    is_completed = models.BooleanField(default=False)
    viewed_time = models.IntegerField(default=0)

    class Meta:  # NOQA
        unique_together = ('course', 'user_id', 'video_block_id')

    def __unicode__(self):  # NOQA
        return u'{} {} {}'.format(self.user_id, self.course, self.video_block_id)


class VideoViewsByBlock(models.Model):
    """
    Block's Video Views info.
    """

    course = CourseKeyField(max_length=255, db_index=True)
    video_block_id = models.CharField(max_length=255, db_index=True)
    count_full_viewed = models.IntegerField(default=0)
    count_part_viewed = models.IntegerField(default=0)
    video_duration = models.IntegerField(default=0)

    class Meta:  # NOQA
        unique_together = ('course', 'video_block_id')

    def __unicode__(self):  # NOQA
        return u'{} {}'.format(self.course, self.video_block_id)


class VideoViewsByDay(models.Model):
    """
    Day's Video Views info.
    """

    course = CourseKeyField(max_length=255, db_index=True)
    video_block_id = models.CharField(max_length=255, db_index=True)
    day = models.DateField(db_index=True)
    total = models.IntegerField(default=0)
    users_ids = models.TextField(blank=True, null=True, validators=[validate_comma_separated_integer_list])

    class Meta:  # NOQA
        unique_together = ('course', 'video_block_id', 'day')

    def __unicode__(self):  # NOQA
        return u'{}, {}, day - {}'.format(self.course, self.video_block_id, self.day)


class DiscussionActivity(models.Model):
    """
    Track specific user activities.
    """

    event_type = models.CharField(max_length=255)
    user_id = models.IntegerField(db_index=True)
    course = CourseKeyField(max_length=255, db_index=True)
    category_id = models.CharField(max_length=255, blank=True, null=True)
    commentable_id = models.CharField(max_length=255, db_index=True)
    discussion_id = models.CharField(max_length=255)
    thread_type = models.CharField(max_length=255, blank=True, null=True)
    log_time = models.DateTimeField()

    def __unicode__(self):  # NOQA
        return u'{},  {},  user_id - {}'.format(self.event_type, self.course, self.user_id)


class DiscussionActivityByDay(models.Model):
    """
    Day's Discussion Activities info.
    """

    course = CourseKeyField(max_length=255, db_index=True)
    day = models.DateField(db_index=True)
    total = models.IntegerField(default=0)

    class Meta:  # NOQA
        unique_together = ('course', 'day')

    def __unicode__(self):  # NOQA
        return u'{},  day - {}'.format(self.course, self.day)
