from django.contrib import admin
from .models import TravelRequest, ApprovalEvent


class ApprovalEventInline(admin.TabularInline):
    model = ApprovalEvent
    extra = 0
    readonly_fields = ("step_number", "function", "actor", "decision", "comment", "ip_address", "created_at")
    can_delete = False


@admin.register(TravelRequest)
class TravelRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "applicant", "step1_function", "status", "created_at")
    list_filter = ("status", "step1_function")
    search_fields = ("applicant__username", "applicant__email")
    inlines = [ApprovalEventInline]


@admin.register(ApprovalEvent)
class ApprovalEventAdmin(admin.ModelAdmin):
    list_display = ("request", "step_number", "function", "actor", "decision", "created_at")
    list_filter = ("decision", "function")
    search_fields = ("request__id", "actor__username", "actor__email")
    readonly_fields = ("created_at",)
