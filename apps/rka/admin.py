from django.contrib import admin
from .models import TravelRequest, ExpenseItem

class ExpenseItemInline(admin.TabularInline):
    model = ExpenseItem
    extra = 0

@admin.register(TravelRequest)
class TravelRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "applicant", "origin", "destination", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "applicant__email", "origin", "destination")
    inlines = [ExpenseItemInline]

@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ("id", "travel_request", "date", "description", "amount")
    list_filter = ("date",)
    search_fields = ("description",)
