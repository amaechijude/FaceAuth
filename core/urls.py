from django.urls import path
from . import views
urlpatterns = [
    path('register', views.register_user, name='register_user'),
    path('login', views.login_user, name='login_user'),
    path('logout', views.logout_user, name='logout_user'),
    path('', views.index_page, name='index_page'),
    path('prompt', views.get_vacation_recomendation, name='prompt')
]