from django.contrib import admin

from .models import Applicant, Application, Interview, JobPosting

admin.site.register(JobPosting)
admin.site.register(Applicant)
admin.site.register(Application)
admin.site.register(Interview)
