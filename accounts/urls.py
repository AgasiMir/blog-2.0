from django.urls import path

from .import views

urlpatterns = [
    path('user/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('user/<str:slug>/', views.ProfileDetailView.as_view(), name='profile_detail'),

]
