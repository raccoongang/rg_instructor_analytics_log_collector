"""
Models of the rg analytics.
"""

from django.db import connection
from django.db.models import BooleanField, CharField, DateTimeField, IntegerField, Manager, Model, TextField


from openedx.core.djangoapps.xmodule_django.models import CourseKeyField


class BulkInsertManager(Manager):
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


class ProcessedZipLog(Model):
    """
    Model for store processed log files.
    """

    file_name = TextField(max_length=256)


class LogTable(Model):
    """
    Model for store tracking log record inside mySql.
    """

    objects = BulkInsertManager()

    message_type = CharField(db_index=True, max_length=128)
    log_time = DateTimeField()
    user_name = CharField(null=True, blank=True, max_length=128)
    log_message = TextField()

    class Meta:
        """
        Meta class.
        """

        unique_together = ('message_type', 'log_time', 'user_name')
        ordering = ['-log_time']


class EnrollmentByDay(Model):
    """
    Model for the statistic of the enrollment per day.
    """

    day = DateTimeField(db_index=True)
    total = IntegerField()
    enrolled = IntegerField()
    unenrolled = IntegerField()
    course = CourseKeyField(max_length=255, db_index=True)

    class Meta:
        """
        Meta class.
        """

        ordering = ['-day']


class EnrollmentByUser(Model):
    """
    Model for store enroll state of the user.
    """

    course = CourseKeyField(max_length=255, db_index=True)
    student = IntegerField(db_index=True)
    is_enrolled = BooleanField()
