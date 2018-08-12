from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/', include([
        path('password-change/', auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy('login')), name='password_change'),
        path('user-change/<int:pk>/', views.UserChangeView.as_view(), name='user_change')
    ]
    )),
    path('casework/', include('cases.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('', views.home_view, name='home')
]
