from django.contrib import admin
from .models import Workspace, GlobalTemplate, GlobalTemplateField, WorkspaceField, WorkspaceMembership, OrgRoleChangeLog, LabelTemplate, LabelTemplateField


class WorkspaceFieldInline(admin.TabularInline):
    model = WorkspaceField
    extra = 0


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "workspace_code", "created_by", "created_at")
    search_fields = ("name", "workspace_code", "org__name")
    list_filter = ("org",)
    inlines = [WorkspaceFieldInline]


@admin.register(WorkspaceField)
class WorkspaceFieldAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "field_type", "key", "x", "y", "width", "height")
    list_filter = ("field_type", "workspace")
    search_fields = ("name", "key", "workspace__name")

@admin.register(WorkspaceMembership)
class WorkspaceMembershipAdmin(admin.ModelAdmin):
    list_display = ('workspace', 'user', 'role', 'created_at', 'updated_at')
    list_filter = ('workspace', 'role')
    search_fields = ('workspace__name', 'user__email')


@admin.register(OrgRoleChangeLog)
class OrgRoleChangeLogAdmin(admin.ModelAdmin):
    list_display = ('org', 'user', 'previous_role', 'new_role', 'changed_by', 'changed_at')
    list_filter = ('org', 'previous_role', 'new_role')
    search_fields = ('user__email', 'org__name')

@admin.register(LabelTemplate)
class LabelTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'workspace', 'template_code', 'category', 'is_base', 'created_by', 'created_at')
    list_filter = ('workspace', 'category', 'is_base')
    search_fields = ('name', 'workspace__name', 'template_code')


@admin.register(LabelTemplateField)
class LabelTemplateFieldAdmin(admin.ModelAdmin):
    list_display = ('template', 'name', 'field_type', 'order', 'x', 'y', 'width', 'height')
    list_filter = ('template', 'field_type')
    search_fields = ('template__name', 'name')

class GlobalTemplateFieldInline(admin.TabularInline):
    model = GlobalTemplateField
    extra = 0


@admin.register(GlobalTemplate)
class GlobalTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_by", "created_at", "is_active")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "description")
    inlines = [GlobalTemplateFieldInline]