from django.urls import path
from . import views
app_name = 'cases'
urlpatterns = [
    path('intake/', views.IntakeView.as_view(), name='intake'),
    path('case/<str:slug>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('case/<str:slug>/closeopen', views.CaseOpenCloseView.as_view(), name='case_open_close'),
    path('', views.CaseListView.as_view(), name='case_list'),
]
