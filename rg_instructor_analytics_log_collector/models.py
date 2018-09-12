"""
Models of the rg analytics.
"""

from django.db.models import DateTimeField, Model, TextField, CharField, Manager
from django.db import connection


class BulkInsertManager(Manager):
    def bulk_insert_or_update(self, create_fields, update_fields, values):
        if not values or not values[0]:
            return

        cursor = connection.cursor()
        db_table = self.model._meta.db_table

        values_sql = "(%s)" % (','.join(["%s" for _ in range(len(values[0]))]),)
        base_sql = "INSERT INTO %s (%s) VALUES " % (db_table, ",".join(create_fields))
        on_duplicates = [field + "=VALUES(" + field + ")" for field in update_fields ]

        sql = "%s %s ON DUPLICATE KEY UPDATE %s" % (base_sql, values_sql, ",".join(on_duplicates))

        cursor.executemany(sql, values)


class ProcessedZipLog(Model):
    file_name = TextField(max_length=256)


class LogTable(Model):
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
