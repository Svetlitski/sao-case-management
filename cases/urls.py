from django.urls import path

from . import views
app_name = 'cases'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.PersonDetailView.as_view(), name='detail'),
]
