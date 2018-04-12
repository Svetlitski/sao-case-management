from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
app_name = 'cases'
urlpatterns = [
    path('login/', views.OfficeLoginView.as_view(), name='login'),
    path('', views.HomeView.as_view(), name='home'),
    path('logout', views.logout_view, name='logout'),
    #path('caseworkers/', views.IndexView.as_view(), name='index'),
    path('intake/', views.IntakeView.as_view(), name='intake'),
    path('case/<str:slug>/', views.CaseUpdateView.as_view(), name='case_update'),
    path('<str:slug>/', views.PersonDetailView.as_view(), name='detail'),
]
