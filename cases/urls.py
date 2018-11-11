from django.urls import path
from . import views
app_name = 'cases'
urlpatterns = [
    path('intake/', views.IntakeView.as_view(), name='intake'),
    path('case/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('case/<int:pk>/change', views.CaseChangeView.as_view(), name='case_change'),
    path('case/<int:pk>/closeopen', views.CaseOpenCloseView.as_view(), name='case_open_close'),
    path('', views.CaseListView.as_view(), name='case_list'),
]
