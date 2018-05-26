from django.urls import path
from . import views
app_name = 'cases'
urlpatterns = [
    path('login/', views.OfficeLoginView.as_view(), name='login'),
    path('', views.home_view, name='home'),
    path('logout', views.logout_view, name='logout'),
    path('intake/', views.IntakeView.as_view(), name='intake'),
    path('case/<str:slug>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('case/<str:slug>/close', views.CaseCloseView.as_view(), name='case_close'),
    path('<str:slug>/', views.CaseListView.as_view(), name='case_list'),
]
