from typing import Any, Dict
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.urls import reverse_lazy

from apps.blog.models import Post

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, UserCreationForm, UserLoginForm


class ProfileDetailView(DetailView):
    """
    Представление для просмотра профиля
    """
    model = get_user_model()
    context_object_name = 'profile'
    template_name = 'accounts/profile_detail.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f"Профиль пользователя: {self.object.username}"
        posts = Post.custom.filter(author__slug=self.kwargs['slug'])
        context['posts'] = posts[:5]
        context['count'] = len(posts)
        return context


class ProfileUpdateView(UpdateView):
    """
    Представление для редактирования профиля
    """
    model = get_user_model()
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'slug': self.object.slug})


class UserRegisterView(SuccessMessageMixin, CreateView):
    """
    Представление регистрации на сайте с формой регистрации
    """
    form_class = UserRegisterForm
    template_name = 'accounts/user_register.html'
    success_message = 'Вы успешно зарегистрировались. Можете войти на сайт!'
    success_url = reverse_lazy('login')
    extra_context = {'title': 'Регистрация на сайте'}


class UserLoginView(SuccessMessageMixin, LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/user_login.html'
    next_page = 'home'
    success_message = "Добро пожаловать на сайт, %(res)s!"
    extra_context = {'title': 'Авторизация на сайте'}

    def get_success_message(self, cleaned_data: Dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, res=self.request.user)


class UserLogoutView(LogoutView):
    """
    Выход с сайта
    """
    next_page = 'home'
