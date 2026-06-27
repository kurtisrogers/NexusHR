from django.contrib import admin

from .models import AttendanceRecord, WorkSchedule

admin.site.register(WorkSchedule)
admin.site.register(AttendanceRecord)
