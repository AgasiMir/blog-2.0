from typing import Dict, Any
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from apps.blog.models import Post, Category
from apps.blog.forms import PostCreateForm
from ..services.mixins import AuthorRequiredMixin


class PaginationMixin:
    template_name = "blog/post_list.html"
    context_object_name = 'posts'
    symbol = ''

    def get_paginate_by(self, queryset):
        if '12' in self.request.GET:
            self.__class__.symbol += 'X'

        if '8' in self.request.GET:
            self.__class__.symbol += 'Y'

        if len(self.__class__.symbol) > 10:
            self.__class__.symbol = self.__class__.symbol[-1]

        try:
            if self.__class__.symbol[-1] == 'X':
                self.paginate_by = 12
            elif self.__class__.symbol[-1] == 'Y':
                self.paginate_by = 8
        except IndexError:
            self.paginate_by = 8

        return self.paginate_by

    def get_mixin_context(self, context):
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(
            page.number,
            on_each_side=2,
            on_ends=1
        )
        return context


class PostListView(PaginationMixin, ListView):
    queryset = Post.custom.all()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Главная страница"

        return self.get_mixin_context(context)


class PostDetailView(DetailView):
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # context['title'] = context['post'].title
        context["title"] = self.object.title
        return context

    def get_object(self, queryset=None):
        # post = get_object_or_404(Post, slug=self.kwargs["slug"])
        post = Post.custom.get(slug=self.kwargs['slug'])    #такой запрос лучше оптимизирован

        post.views += 1
        post.save()

        return post


class PostFromCategory(PaginationMixin, ListView):
    category = None

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs["slug"])
        queryset = Post.custom.filter(category__slug=self.category.slug)
        if not queryset:
            sub_cat = Category.objects.filter(parent=self.category)
            queryset = Post.custom.filter(category__in=sub_cat)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = f"Записи из категории: {self.category.title}"
        return self.get_mixin_context(context)


class PostsByAuthorView(PaginationMixin, ListView):
    """
    Статьи по авторам
    """

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        author = get_user_model().objects.get(slug=self.kwargs['slug'])
        context['title'] = f"Статьи автора {author}"
        return self.get_mixin_context(context)

    def get_queryset(self) :
        return Post.custom.filter(author__slug=self.kwargs['slug'])


class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'blog/post_create.html'
    form_class = PostCreateForm
    extra_context = {'title': 'Добавление статьи на сайт'}
    login_url = 'home'
    success_message = 'Запись была успешно добавлена!'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Post
    template_name = 'blog/post_update.html'
    form_class = PostCreateForm
    context_object_name = 'post'
    login_url = 'home'
    success_message = 'Запись была успешно обновлена!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Обновление статьи {context['post'].title}"
        # context['title'] = f'Обновление статьи: {self.object.title}'
        return context
