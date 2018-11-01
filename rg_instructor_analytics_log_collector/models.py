"""
Models of the RG analytics.
"""

from django.db import connection, models

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

from rg_instructor_analytics_log_collector.constants import Events


class BulkInsertManager(models.Manager):
    """
    Manager with  bulk_insert_or_update.
    """

    def bulk_insert_or_update(self, create_fields, update_fields, values):
        """
        Insert or update series of the records.

        :param create_fields: fields, that must be created.
        :param update_fields: fields, that must be updated in case of unique conflict.
        :param values: the matrix where each row represent new record and
        each column represents values from create_fields(in the same order).
        """
        if not values or not values[0]:
            return

        cursor = connection.cursor()
        db_table = self.model._meta.db_table

        values_sql = "(%s)" % (','.join(['%s'] * len(values[0])),)
        base_sql = "INSERT INTO %s (%s) VALUES " % (db_table, ",".join(create_fields))
        on_duplicates = ["%s=VALUES(%s)" % (field, field) for field in update_fields]

        sql = "%s %s ON DUPLICATE KEY UPDATE %s" % (base_sql, values_sql, ",".join(on_duplicates))

        cursor.executemany(sql, values)


class ProcessedZipLog(models.Model):
    """
    Already processed tracking log files.
    """

    file_name = models.TextField(max_length=256)


class LogTable(models.Model):
    """
    Log Records parsed from tracking gzipped log file.
    """

    message_type = models.CharField(db_index=True, max_length=128)
    log_time = models.DateTimeField()
    user_name = models.CharField(null=True, blank=True, max_length=128)
    log_message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    objects = BulkInsertManager()

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
    total = models.IntegerField()
    enrolled = models.IntegerField()
    unenrolled = models.IntegerField()
    course = CourseKeyField(max_length=255, db_index=True)
    last_updated = models.DateField(auto_now=True, null=True)

    class Meta:  # NOQA
        unique_together = ('course', 'day',)
        ordering = ['-day']


class EnrollmentByUser(models.Model):
    """
    User's Enrollment status changes (per-course).
    """

    course = CourseKeyField(max_length=255, db_index=True)
    student = models.IntegerField(db_index=True)
    is_enrolled = models.BooleanField()


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

    course = CourseKeyField(max_length=255)
    user_id = models.IntegerField()
    video_block_id = models.CharField(max_length=255)
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

    course = CourseKeyField(max_length=255)
    video_block_id = models.CharField(max_length=255)
    count_full_viewed = models.IntegerField(default=0)
    count_part_viewed = models.IntegerField(default=0)
    video_duration = models.IntegerField(default=0)

    class Meta:  # NOQA
        unique_together = ('course', 'video_block_id')

    def __unicode__(self):  # NOQA
        return u'{} {}'.format(self.course, self.video_block_id)


class DiscussionActivity(models.Model):
    """
    Track specific user activities
    """

    event_type = models.CharField(max_length=255)
    user_id = models.IntegerField()
    course = CourseKeyField(max_length=255, db_index=True)
    category_id = models.CharField(max_length=255, blank=True, null=True)
    commentable_id = models.CharField(max_length=255)
    discussion_id = models.CharField(max_length=255)
    thread_type = models.CharField(max_length=255, blank=True, null=True)
    log_time = models.DateTimeField()

    def __unicode__(self):  # NOQA
        return u'{},  {},  user_id - {}'.format(self.event_type, self.course, self.user_id)
