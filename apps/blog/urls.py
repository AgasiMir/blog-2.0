from django.urls import path

from . import views


urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:slug>/', views.PostFromCategory.as_view(), name='post_by_category'),
]
