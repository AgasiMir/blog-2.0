from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import FileExtensionValidator


class Post(models.Model):
    """
    Модель постов для нашего блога
    """

    STATUS_OPTIONS = (("published", "Опубликовано"), ("draft", "Черновик"))

    title = models.CharField(verbose_name="Название записи", max_length=255)
    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True)
    description = models.TextField(verbose_name="Краткое описание", max_length=500)
    text = models.TextField(verbose_name="Полный текст записи")
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
        choices=STATUS_OPTIONS, default="published", verbose_name="Статус записи"
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
    fixed = models.BooleanField(verbose_name='Прикреплено', default=False)
    views = models.PositiveBigIntegerField(verbose_name='Количество просмотров', default=0)

    class Meta:
        db_table = 'blog_post'
        ordering = ['-fixed', '-create']
        indexes = [models.Index(fields=['-fixed', '-create', 'status'])]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self) -> str:
        return self.title
