from django.urls import path

from . import views
app_name = 'cases'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('caseworkers/', views.IndexView.as_view(), name='index'),
    path('intake', views.IntakeView.as_view(), name='intake'),
    path('<str:slug>', views.PersonDetailView.as_view(), name='detail'),
]
