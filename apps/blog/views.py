from typing import Dict, Any
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView

from apps.blog.models import Post, Category


class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "blog/post_list.html"
    paginate_by = 5

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Главная страница"
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
        return context


class PostDetailView(DetailView):
    # model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # context['title'] = context['post'].title
        context["title"] = self.object.title
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, slug=self.kwargs["slug"])

        post.views += 1
        post.save()

        return post


class PostFromCategory(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    category = None
    paginate_by = 5

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs["slug"])
        queryset = Post.objects.filter(category__slug=self.category.slug)
        if not queryset:
            sub_cat = Category.objects.filter(parent=self.category)
            queryset = Post.objects.filter(category__in=sub_cat)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = f"Записи из категории: {self.category.title}"
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
        return context
