from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display: tuple[str, str, str, str, str] = (
        "pk",
        "username",
        "bio",
        "email",
        "role",
    )
    list_display_links: tuple[str, str, str] = (
        "pk",
        "username",
        "email",
    )
    search_fields: tuple[str, str] = ("username", "email", )
    list_editable: tuple[str] = ("role", )
    list_filter: tuple[str] = ("role", )
    empty_value_display: str = "-пусто-"
