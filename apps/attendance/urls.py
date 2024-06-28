from time import pthread_getcpuclockid
from django.urls import path , include
from . import views
from django.views.generic.base import TemplateView

app_name = "apps.attendance"

urlpatterns = [
    path("",TemplateView.as_view(template_name="manager_dash.html"),name="home"),
    path("requests/",views.LeaveRequestView.as_view(),name="leaveRequest"),
    path("requestAPI/",views.LeaveRequestAPIView.as_view(),name="leaveRequestAPI"),
    path('leave/<int:leave_id>/approve/', views.approve_leave, name='approve_leave'),
    path('leave/<int:leave_id>/reject/', views.reject_leave, name='reject_leave'),
    path('overview/',TemplateView.as_view(template_name='manager_overview.html'),name="overview"),
]