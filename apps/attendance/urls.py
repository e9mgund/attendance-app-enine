# from time import pthread_getcpuclockid
from django.urls import path, include
from . import views
from django.views.generic.base import TemplateView

app_name = "apps.attendance"

urlpatterns = [
    path(
        "managerdash/",
        views.DashboardView.as_view(),
        name="home",
    ),
    path('',views.EmployeeDashboard.as_view(),name="emp_dash"),
    path("requests/", views.LeaveRequestView.as_view(), name="leaveRequest"),
    path(
        "requestAPI/",
        views.LeaveRequestAPIView.as_view(),
        name="leaveRequestAPI",
    ),
    path(
        "leave/<int:leave_id>/approve/",
        views.approve_leave,
        name="approve_leave",
    ),
    path(
        "leave/<int:leave_id>/reject/", views.reject_leave, name="reject_leave"
    ),
    path(
        "overview/",
        views.OverviewView.as_view(),
        name="overview",
    ),
    path(
        "employee/",
        TemplateView.as_view(template_name="employee_overview.html"),
        name="employee",
    ),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("markattendance/",views.MarkAttendanceView.as_view(),name="markAttendance"),
    path("report/",views.generate_graph,name="report"),
]
