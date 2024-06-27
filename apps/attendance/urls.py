from django.urls import path , include
from . import views
from django.views.generic.base import TemplateView

app_name = "apps.attendance"

urlpatterns = [
    path("",TemplateView.as_view(template_name="manager_dash.html"),name="home"),
    path("requests/",views.LeaveRequestView.as_view(),name="leaveRequest"),
    path("requestAPI/",views.LeaveRequestAPIView.as_view(),name="leaveRequestAPI"),
]