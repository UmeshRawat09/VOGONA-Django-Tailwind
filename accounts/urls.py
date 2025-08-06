from django.urls import path
from . import views

urlpatterns = [
    path('sign_up/', views.sign_up, name='sign_up'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.account , name='account'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_message/<uidb64>/<token>/', views.reset_password_message, name='reset_password_message'),
    path('reset_password/', views.reset_password, name='reset_password'),
]
