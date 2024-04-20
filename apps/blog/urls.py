from django.urls import path

from . import views


urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<str:slug>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:slug>/', views.PostFromCategory.as_view(), name='post_by_category'),
    path('author-posts/<str:slug>/', views.PostsByAuthorView.as_view(), name='posts_by_author'),
]
