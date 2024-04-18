from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.forms import ValidationError



UPDATE_FORM_WIDGET = forms.TextInput(attrs={"class": "form-control mb-1"})


class UserUpdateForm(forms.ModelForm):
    """
    Форма обновления данных пользователя
    """

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": UPDATE_FORM_WIDGET,
            "email": UPDATE_FORM_WIDGET,
            "first_name": UPDATE_FORM_WIDGET,
            "last_name": UPDATE_FORM_WIDGET,
        }

    def clean_email(self):
        """
        Форма обновления данных пользователя
        """
        email = self.cleaned_data.get("email")
        username = self.cleaned_data.get("username")
        if (
            email
            and get_user_model()
            .objects.filter(email=email)
            .exclude(username=username)
            .exists()
        ):
            raise ValidationError("Email адрес должен быть уникальным")
        return email


class ProfileUpdateForm(forms.ModelForm):
    this_year = date.today().year
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.SelectDateWidget(
            years=tuple(range(this_year - 100, this_year - 5))
        ),
    )
    bio = forms.CharField(
        label="О себе",
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 5, "class": "form-control mb-1"}),
    )
    avatar = forms.ImageField(
        label="Аватар",
        widget=forms.FileInput(attrs={"rows": 5, "class": "form-control mb-1"}),
    )

    class Meta:
        model = get_user_model()
        fields = ['bio', 'birth_date', 'avatar']
