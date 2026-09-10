from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "author",
        "published_at",
        "is_published",
        "view_count",
    )

    list_filter = (
        "category",
        "is_published",
        "published_at",
    )

    search_fields = (
        "title",
        "summary",
        "content",
        "slug",
    )

    readonly_fields = (
        "slug",
        "published_at",
        "updated_at",
        "view_count",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    ordering = ("-published_at",)