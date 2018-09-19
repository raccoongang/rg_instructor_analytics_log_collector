"""
Admin site bindings for rg_instructor_analytics app.
"""

from django.contrib import admin

from rg_instructor_analytics_log_collector import models


admin.site.register(models.ProcessedZipLog, admin.ModelAdmin)
admin.site.register(models.LogTable, admin.ModelAdmin)
admin.site.register(models.EnrollmentByDay, admin.ModelAdmin)
admin.site.register(models.EnrollmentByUser, admin.ModelAdmin)
