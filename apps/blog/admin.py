from django.contrib import admin
from django.db.models import F
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin
from django_mptt_admin.admin import DjangoMpttAdmin

from .models import Post, Category


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    """
    Админ-панель модели категорий
    """

    prepopulated_fields = {"slug": ("title",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Админ-панель модели статей
    """

    list_display = ["photo", "title", "category", "author", "create"]
    list_display_links = ["photo", "title"]
    list_filter = ["status", "create", "category", "author"]
    search_fields = ["title", "text", "description"]

    list_per_page = 10
    actions = ["boost"]

    save_on_top = True
    readonly_fields = ["photo"]
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Изображение")
    def photo(self, post: Post):
        if post.thumbnail:
            return mark_safe(f"<img src='{post.thumbnail.url}' width=120>")
        return "Нет изображения"

    @admin.action(description="Больше просмотров")
    def boost(self, request, queryset):
        post = queryset.update(views=F("views") + 200_000)
        self.message_user(request, f"Больше просмотров применено к: {post} постам(у))")
