from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models import TextField
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey


from apps.services.utils import unique_slugify


class PostManager(models.Manager):
    """
    Кастомный менеджер для модели постов
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "author")
            .prefetch_related("ratings")
            .filter(status="published")
        )


class CommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("author", "post", "parent")


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
    views = models.PositiveBigIntegerField(verbose_name="Просмотров", default=0)

    objects = models.Manager()
    custom = PostManager()

    class Meta:
        db_table = "blog_post"
        ordering = ["-fixed", "-create"]
        indexes = [models.Index(fields=["-fixed", "-create", "status"])]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        """
        При сохранении генерируем слаг и проверяем на уникальность
        """

        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def correct_views(self):
        if self.views < 1000:
            return self.views
        if self.views >= 1000:
            res = f"{self.views:_}"
            res = res.replace("_", ".")
            res = res[: res.index(".") + 2]
            if res[-1] == "0":
                return res[:-2] + "K"
            return res + "K"

    def get_sum_rating(self):
        return sum([rating.value for rating in self.ratings.all()])


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

    def get_absolute_url(self):
        return reverse("post_by_category", kwargs={"slug": self.slug})

    def __str__(self):
        """
        Возвращение заголовка категории
        """
        return self.title


class Comment(MPTTModel):
    """
    Модель древовидных комментариев
    """

    STATUS_OPTIONS = (("published", "Опубликовано"), ("draft", "Черновик"))

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, verbose_name="Запись", related_name="comments"
    )
    author = models.ForeignKey(
        get_user_model(),
        verbose_name="Автор комментария",
        on_delete=models.CASCADE,
        related_name="comments_author",
    )
    content = TextField(
        verbose_name="Текст комментария",
        max_length=3000,
    )
    time_create = models.DateTimeField(
        auto_now_add=True, verbose_name="Время добавления"
    )
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    status = models.CharField(
        choices=STATUS_OPTIONS,
        default="published",
        verbose_name="Статус поста",
        max_length=10,
    )
    parent = TreeForeignKey(
        "self",
        verbose_name="Родительский комментарий",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )

    objects = CommentManager()

    class MPTTMeta:
        """
        Сортировка по вложенности
        """

        order_insertion_by = "time_create"

    class Meta:
        """
        Сортировка, название модели в админ панели
        """

        ordering = ["time_create"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"{self.author}:{self.content}"


class Rating(models.Model):
    """
    Модель рейтинга: Лайк - Дизлайк
    """

    post = models.ForeignKey(
        Post,
        verbose_name="Запись",
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    user = models.ForeignKey(
        get_user_model(),
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    value = models.IntegerField(
        verbose_name="Значение", choices=[(1, "Нравится"), (-1, "Не нравится")]
    )
    time_create = models.DateTimeField(
        verbose_name="Время добавления", auto_now_add=True
    )
    ip_address = models.GenericIPAddressField(verbose_name="IP Адрес")

    class Meta:
        unique_together = ("post", "ip_address")
        ordering = ["-time_create"]
        indexes = [models.Index(fields=["-time_create", "value"])]
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"

    def __str__(self) -> str:
        return self.post.title
