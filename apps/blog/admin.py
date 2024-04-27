from random import randint
from django.contrib import admin
from django.db.models import F
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin
from django_mptt_admin.admin import DjangoMpttAdmin
from django_summernote.admin import SummernoteModelAdmin

from .models import Post, Category, Comment


class CommentInLine(admin.StackedInline):
    model = Comment
    extra = 0
    readonly_fields = ["content", "author", "parent"]


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    """
    Админ-панель модели категорий
    """

    prepopulated_fields = {"slug": ("title",)}


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    """
    Админ-панель модели статей
    """

    list_display = [
        "photo",
        "tr_title",
        "category",
        "author",
        "views",
        "get_comments_count",
        "create",
    ]
    list_display_links = ["photo", "tr_title"]
    list_filter = ["status", "create", "category", "author"]
    search_fields = ["title", "text", "description", "author__username"]

    list_per_page = 10
    actions = ["boost"]

    save_on_top = True
    exclude = ["slug"]
    fields = [
        "photo_detail",
        "title",
        "description",
        "text",
        "category",
        "thumbnail",
        "status",
        "author",
        "updater",
        "fixed",
        "views",
    ]
    readonly_fields = ["photo_detail"]
    inlines = [CommentInLine]
    # prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Изображение")
    def photo(self, post: Post):
        if post.thumbnail:
            return mark_safe(f"<img src='{post.thumbnail.url}' width=120>")
        return "Нет изображения"

    @admin.display(description="Изображение Поста")
    def photo_detail(self, post: Post):
        if post.thumbnail:
            return mark_safe(f"<img src='{post.thumbnail.url}' width=400>")
        return "Нет изображения"

    @admin.display(description="Комментариев")
    def get_comments_count(self, post: Post):
        return post.comments.count()

    @admin.display(description="Заголовок")
    def tr_title(self, post: Post):
        return post.title[:50] + "..." if len(post.title) > 50 else post.title

    @admin.action(description="Больше просмотров")
    def boost(self, request, queryset):
        random_number = randint(5500, 15400)
        post = queryset.update(views=F("views") + 50_000 + random_number)
        self.message_user(request, f"Больше просмотров применено к: {post} постам(у)")


@admin.register(Comment)
class CommentAdmin(DraggableMPTTAdmin):
    """
    Админ-панель модели комментариев
    """

    list_display = ["post", "indented_title"]
