from django.contrib import admin

from .models import Employee, EmployeeDocument


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "user", "department", "job_title", "status", "hire_date"]
    list_filter = ["status", "employment_type", "department"]
    search_fields = ["employee_id", "user__first_name", "user__last_name", "user__email"]
    inlines = [EmployeeDocumentInline]
