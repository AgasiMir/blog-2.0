from typing import Dict, Any
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import F
from django.views.generic import CreateView, ListView, DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from apps.blog.models import Post, Category, Comment, Rating
from apps.blog.forms import PostCreateForm, CommentCreateForm
from ..services.mixins import AuthorRequiredMixin



class PaginationMixin:
    template_name = "blog/post_list.html"
    context_object_name = 'posts'
    symbol = 'Y'

    def get_paginate_by(self, queryset):
        if '12' in self.request.GET:
            self.__class__.symbol += 'X'

        if '8' in self.request.GET:
            self.__class__.symbol += 'Y'

        if len(self.__class__.symbol) > 10:
            self.__class__.symbol = self.__class__.symbol[-1]


        if self.__class__.symbol[-1] == 'X':
            self.paginate_by = 12
        elif self.__class__.symbol[-1] == 'Y':
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
        context['form'] = CommentCreateForm
        context['comments_filter'] = Comment.objects.filter(post=self.object, status='published')
        # context['views'] = Post.custom.filter(slug=self.kwargs['slug']).update(views=F('views') + 1)
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


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': comment.time_create.strftime('%Y-%b-%d %H:%M:%S'),
                'avatar': comment.author.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.get_absolute_url()
            }, status=200)

        return redirect(comment.post.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse({'error': 'Необходимо авторизоваться для добавления комментариев'}, status=400)


class RatingCreateView(View):
    model = Rating

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        value = int(request.POST.get('value'))
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        ip_address = ip
        user = request.user if request.user.is_authenticated else None

        rating, created = self.model.objects.get_or_create(
           post_id=post_id,
            ip_address=ip_address,
            defaults={'value': value, 'user': user},
        )

        if not created:
            if rating.value == value:
                rating.delete()
                return JsonResponse({'status': 'deleted', 'rating_sum': rating.post.get_sum_rating()})
            else:
                rating.value = value
                rating.user = user
                rating.save()
                return JsonResponse({'status': 'updated', 'rating_sum': rating.post.get_sum_rating()})
        return JsonResponse({'status': 'created', 'rating_sum': rating.post.get_sum_rating()})


#handlers


def tr_handler404(request, exception):
    """
    Обработка ошибки 404
    """
    return render(request=request, template_name='errors/error_page.html', status=404, context={
        'title': 'Страница не найдена: 404',
        'error_message': 'К сожалению такая страница была не найдена, или перемещена',
    })


def tr_handler500(request):
    """
    Обработка ошибки 500
    """
    return render(request=request, template_name='errors/error_page.html', status=500, context={
        'title': 'Ошибка сервера: 500',
        'error_message': 'Внутренняя ошибка сайта, вернитесь на главную страницу, отчет об ошибке мы направим администрации сайта',
    })


def tr_handler403(request, exception):
    """
    Обработка ошибки 403
    """
    return render(request=request, template_name='errors/error_page.html', status=403, context={
        'title': 'Ошибка доступа: 403',
        'error_message': 'Доступ к этой странице ограничен',
    })
