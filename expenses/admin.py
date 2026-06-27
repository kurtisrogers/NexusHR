from django.contrib import admin

from .models import ExpenseCategory, ExpenseClaim

admin.site.register(ExpenseCategory)
admin.site.register(ExpenseClaim)
