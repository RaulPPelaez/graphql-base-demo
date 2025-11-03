from django.contrib import admin
from .models import DeployedApp


@admin.register(DeployedApp)
class DeployedAppAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'active', 'created_at']
    list_filter = ['active']
    search_fields = ['id', 'owner__username']
    readonly_fields = ['id', 'created_at']
