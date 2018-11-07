"""
Models of the RG analytics.
"""

from django.db import connection, models

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
    user_name = models.CharField(max_length=255, null=True, blank=True,  db_index=True)
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
    STUDENT_STEP = 'ST'

    PROCESSOR_CHOICES = (
        (ENROLLMENT, 'Enrollment'),
        (VIDEO_VIEWS, 'VideoViews'),
        (DISCUSSION_ACTIVITY, 'Discussion activity'),
        (STUDENT_STEP, 'Student step'),
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
    Track specific user activities.
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


class StudentStepCourse(models.Model):
    """
    Track student's path through the course.
    """
    event_type = models.CharField(max_length=255)
    user_id = models.IntegerField(db_index=True)
    course = CourseKeyField(max_length=255, db_index=True)
    subsection_id = models.CharField(max_length=255)
    current_unit = models.CharField(max_length=255)
    target_unit = models.CharField(max_length=255)
    log_time = models.DateTimeField()

    def __unicode__(self):  # NOQA
        return u'{},  {},  user_id - {}'.format(self.event_type, self.course, self.user_id)
