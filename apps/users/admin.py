from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "plan", "created_at"]
    list_filter = ["plan"]
    search_fields = ["username", "id"]
    readonly_fields = ["id", "created_at"]
