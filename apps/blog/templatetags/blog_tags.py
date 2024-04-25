from django.db.models import Count
from django.template import Library

from ..models import Post, Comment

register = Library()


@register.inclusion_tag("blog/most_popular.html")
def most_popular():
    return {"posts": Post.custom.order_by("-views")[:5]}


@register.inclusion_tag("blog/most_commented.html")
def most_commented():
    posts = (
        Post.custom.annotate(total=Count("comments"))
        .filter(total__gte=1)
        .order_by("-total")[:5]
    )
    return {"posts": posts}
