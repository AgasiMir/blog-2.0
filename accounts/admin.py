from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['ava', 'username', 'birth_date']
    list_display_links = ['ava', 'username']

    @admin.display(description='Аватар')
    def ava(self, user: Profile):
        if user.avatar:
            return mark_safe(f"<img src='{user.avatar.url}' width=80>")
        return "Нет фото"
