from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import FileExtensionValidator
from mptt.models import MPTTModel, TreeForeignKey


class Post(models.Model):
    """
    Модель постов для нашего блога
    """

    STATUS_OPTIONS = (("published", "Опубликовано"), ("draft", "Черновик"))

    title = models.CharField(verbose_name="Название записи", max_length=255)
    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True)
    description = models.TextField(verbose_name="Краткое описание", max_length=500)
    text = models.TextField(verbose_name="Полный текст записи")
    category = TreeForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="posts",
        verbose_name="Категория",
    )
    thumbnail = models.ImageField(
        default="default.jpg",
        verbose_name="Изображение записи",
        blank=True,
        upload_to="images/thumbnails/%Y/%m/%d",
        validators=[
            FileExtensionValidator(
                allowed_extensions=("png", "jpg", "jpeg", "webp", "gif")
            )
        ],
    )
    status = models.CharField(
        choices=STATUS_OPTIONS,
        default="published",
        verbose_name="Статус записи",
        max_length=10,
    )
    create = models.DateTimeField(verbose_name="Время добавления", auto_now_add=True)
    update = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    author = models.ForeignKey(
        to=get_user_model(),
        verbose_name="Автор",
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name="author_posts",
    )
    updater = models.ForeignKey(
        to=get_user_model(),
        verbose_name="Обновил",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updater_posts",
    )
    fixed = models.BooleanField(verbose_name="Прикреплено", default=False)
    views = models.PositiveBigIntegerField(
        verbose_name="Количество просмотров", default=0
    )

    class Meta:
        db_table = "blog_post"
        ordering = ["-fixed", "-create"]
        indexes = [models.Index(fields=["-fixed", "-create", "status"])]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self) -> str:
        return self.title


class Category(MPTTModel):
    """
    Модель категорий с вложенностью
    """

    title = models.CharField(max_length=255, verbose_name="Название категории")
    slug = models.SlugField(max_length=255, verbose_name="URL категории", blank=True)
    description = models.TextField(verbose_name="Описание категории", max_length=300)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name="children",
        verbose_name="Родительская категория",
    )

    class MPTTMeta:
        """
        Сортировка по вложенности
        """

        order_insertion_by = "title"

    class Meta:
        """
        Сортировка, название модели в админ панели, таблица c данными
        """

        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        db_table = "app_categories"

    def __str__(self):
        """
        Возвращение заголовка категории
        """
        return self.title
