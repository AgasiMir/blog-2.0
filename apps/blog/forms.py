from django import forms
from .models import Post, Comment

from django_summernote.widgets import SummernoteWidget



class PostCreateForm(forms.ModelForm):
    """
    Форма добавления статей на сайте
    Я также использую данную форму для обновления статей
    """
    text = forms.CharField(widget=SummernoteWidget())

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

class CommentCreateForm(forms.ModelForm):
    """
    Форма добавления комментариев к статьям
    """
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='',widget=forms.Textarea(
        attrs={'cols': 30, 'rows': 5, 'placeholder': 'Комментарий', 'class': 'form-control'}))

    class Meta:
        model = Comment
        fields = ['content']
