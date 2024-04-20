from django import forms
from .models import Post


class PostCreateForm(forms.ModelForm):
    """
    Форма добавления статей на сайте
    Я также использую данную форму для обновления статей
    """

    class Meta:
        model = Post
        fields = ["title", "category", "description", "text", "thumbnail"]

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "form-control", "autocomplete": "off"}
            )