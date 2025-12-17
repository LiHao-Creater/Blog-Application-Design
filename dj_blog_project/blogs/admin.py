from django.contrib import admin
from .models import BlogPost, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "date_added", "is_published")
    list_filter = ("is_published", "date_added", "tags")
    search_fields = ("title", "text", "owner__username")
    autocomplete_fields = ("tags",)
