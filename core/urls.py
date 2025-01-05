from django.urls import path
from . import views
urlpatterns = [
    path('user/register', views.register_user, name='register_user'),
    path('user/login', views.login_user, name='login_user'),
    path('index', views.index_page, name='index_page')
]