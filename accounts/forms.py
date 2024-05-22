from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ValidationError

from django_recaptcha.fields import ReCaptchaField



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


class UserRegisterForm(UserCreationForm):
    """
    Переопределенная форма регистрации пользователей
    """

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def clean_email(self):
        """
        Проверка email на уникальность
        """
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and get_user_model().objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Такой email уже используется в системе')
        return email

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы регистрации
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({"placeholder": "Придумайте свой логин"})
        self.fields['email'].widget.attrs.update({"placeholder": "Введите свой email"})
        self.fields['first_name'].widget.attrs.update({"placeholder": "Ваше имя"})
        self.fields['last_name'].widget.attrs.update({"placeholder": "Ваша фамилия"})
        self.fields['password1'].widget.attrs.update({"placeholder": "Придумайте свой пароль"})
        self.fields['password2'].widget.attrs.update({"placeholder": "Повторите придуманный пароль"})
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control", "autocomplete": "off"})


class UserLoginForm(AuthenticationForm):
    """
    Форма авторизации на сайте
    """
    recaptcha = ReCaptchaField()

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'recaptcha']

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы регистрации
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Логин пользователя'
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль пользователя'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'Логин'
