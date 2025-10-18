from django.contrib import admin
from .models import Function, Role, ModuleRoleAssignment

@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "module")
    list_filter = ("module",)
    search_fields = ("name", "code", "module")

@admin.register(ModuleRoleAssignment)
class ModuleRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "role", "created_at")
    list_filter = ("module", "role")
    search_fields = ("user__email", "user__username")
