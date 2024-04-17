from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from apps.services.utils import unique_slugify


class Profile(AbstractUser):
    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True)
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="images/avatars/%Y/%m/%d",
        default="images/avatars/default.png",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg"))],
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name="Информация о себе")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={"slug": self.slgu})
