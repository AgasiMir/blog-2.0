from django.urls import path

from .import views

urlpatterns = [
    path('user/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('user/<str:slug>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

]
