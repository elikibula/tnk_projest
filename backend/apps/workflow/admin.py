from django.contrib import admin
from apps.core.admin import LocationScopedAdmin
from .models import ApprovalAction,FinalDeclaration
@admin.register(ApprovalAction)
class ApprovalActionAdmin(LocationScopedAdmin):
    list_display=("acted_at","report","action_type","user_full_name","user_role","from_status","to_status")
    list_filter=("action_type","from_status","to_status","acted_at")
    search_fields=("report__village__name_en","user_full_name","user_role","comment")
    list_select_related=("report__village","user")
    date_hierarchy="acted_at"
    readonly_fields=tuple(f.name for f in ApprovalAction._meta.fields)
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False

@admin.register(FinalDeclaration)
class FinalDeclarationAdmin(LocationScopedAdmin):
    list_display=("report","declared_by","acknowledged","declared_at")
    list_filter=("acknowledged","declared_at")
    search_fields=("report__village__name_en","declared_by__username")
    readonly_fields=tuple(f.name for f in FinalDeclaration._meta.fields)
    date_hierarchy="declared_at"
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
