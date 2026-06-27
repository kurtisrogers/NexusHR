from django.contrib import admin

from .models import Goal, PerformanceReview, ReviewCycle

admin.site.register(ReviewCycle)
admin.site.register(Goal)
admin.site.register(PerformanceReview)
