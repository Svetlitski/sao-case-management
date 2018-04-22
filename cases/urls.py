from django.urls import path
from . import views
app_name = 'cases'
urlpatterns = [
    path('login/', views.OfficeLoginView.as_view(), name='login'),
    path('', views.HomeView.as_view(), name='home'),
    path('logout', views.logout_view, name='logout'),
    path('intake/', views.IntakeView.as_view(), name='intake'),
    path('case/<str:slug>/', views.CaseUpdateView.as_view(), name='case_update'),
    path('<str:slug>/', views.CaseListView.as_view(), name='detail'),
]
