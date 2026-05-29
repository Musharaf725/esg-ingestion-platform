from django.contrib import admin

from .models import Organization, TenantUser


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ("user", "organization")
    search_fields = ("user__username", "organization__name")
    list_select_related = ("user", "organization")

