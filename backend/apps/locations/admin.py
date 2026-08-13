from django.contrib import admin
from apps.core.admin import LocationScopedAdmin
from .models import Province, Tikina, Village


@admin.register(Province)
class ProvinceAdmin(LocationScopedAdmin):
    list_display = ("code", "name_en", "name_fj", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name_en", "name_fj")


@admin.register(Tikina)
class TikinaAdmin(LocationScopedAdmin):
    list_display = ("code", "name_en", "name_fj", "province", "is_active")
    list_filter = ("province", "is_active")
    search_fields = ("code", "name_en", "name_fj", "province__name_en")
    autocomplete_fields = ("province",)
    list_select_related = ("province",)


@admin.register(Village)
class VillageAdmin(LocationScopedAdmin):
    list_display = ("code", "name_en", "name_fj", "tikina", "is_active")
    list_filter = ("tikina__province", "tikina", "is_active")
    search_fields = ("code", "name_en", "name_fj", "tikina__name_en", "tikina__province__name_en")
    autocomplete_fields = ("tikina",)
    list_select_related = ("tikina__province",)
