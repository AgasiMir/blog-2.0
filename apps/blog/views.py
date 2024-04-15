from typing import Dict, Any
from django.shortcuts import render
from django.views.generic import ListView

from apps.blog.models import Post


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context
