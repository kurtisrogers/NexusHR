from django.contrib import admin

from .models import Announcement, PolicyDocument

admin.site.register(Announcement)
admin.site.register(PolicyDocument)
