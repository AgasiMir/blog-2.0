from django.template import Library

from ..models import Post

register = Library()


@register.inclusion_tag('blog/most_popular.html')
def most_popular():
    return {'posts':Post.custom.order_by('-views')[:5]}
