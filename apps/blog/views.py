from typing import Dict, Any
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView

from apps.blog.models import Post


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context


class PostDetailView(DetailView):
    # model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # context['title'] = context['post'].title
        context['title'] = self.object.title
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, slug=self.kwargs['slug'])

        post.views += 1
        post.save()

        return post
