"""
Admin site bindings for rg_instructor_analytics app.
"""

from django.contrib import admin

from rg_instructor_analytics_log_collector import models


class LastProcessedLogAdmin(admin.ModelAdmin):
    """
    Django admin customizations for LastProcessedLog model.
    """
    list_display = ('processor', 'log_time',)
    raw_id_fields = ('log_table',)

    def log_time(self, obj):
        """
        Customizations for LastProcessedLog model fields.
        """
        return obj.log_table.log_time


admin.site.register(models.ProcessedZipLog, admin.ModelAdmin)
admin.site.register(models.LogTable, admin.ModelAdmin)
admin.site.register(models.EnrollmentByDay, admin.ModelAdmin)
admin.site.register(models.EnrollmentByUser, admin.ModelAdmin)
admin.site.register(models.LastProcessedLog, LastProcessedLogAdmin)
