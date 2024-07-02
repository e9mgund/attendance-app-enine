from typing import Any
from urllib import request
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, ListView
import pytz
from tomlkit import date
from project.settings.settings import LOGOUT_URL
from .models import Employee, LeaveRequest , Attendance , Status
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
import datetime , calendar
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.conf import settings
import json

# Create your views here.


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "manager_dash.html"
    login_url = "/login/"

    def get_context_data(self):
        today = datetime.datetime.now()
        members = list(Employee.objects.filter(manager=self.request.user).values('user_id'))
        if not members:
            pass
        requests = []
        for i in members:
            for j in list(LeaveRequest.objects.values()) :
                if i['user_id'] == j['employee_id'] :
                    j['name'] = str(User.objects.get(pk=j['employee_id']))
                    requests.append(j)
        # print("-----------------")
        # print(requests)
        # print("-----------------")
        return {"weekday":today.strftime("%A"),"date":today.strftime("%d/%m/%Y"),"requests":requests}

class MarkAttendanceView(LoginRequiredMixin,TemplateView) :
    template_name = "mark_attendance.html"
    login_url = "/login/"

    def get_context_data(self):
        employees = Employee.objects.filter(manager=self.request.user)
        return {"date":datetime.datetime.strftime(datetime.datetime.today(),"%Y-%m-%d"),"employees":employees}

    def post(self,request):
        attendance_date,records = request.POST.get("attendance_date"),json.loads(request.POST.get("records"))
        # print(attendance_date,records)
        for record in records:
            # print(type(User.objects.get(username=record['user'])))
            remark = record['remark'] if record['remark'] != "" else str(record['status'])
            user = User.objects.get(username=record['user'])
            # print(record['status'].capitalize())
            status = Status.objects.get(status=record['status'].capitalize())
            # print(type(status))
            update_record,created = Attendance.objects.update_or_create(fordate=attendance_date,employee=user,status=status,remarks=remark)
            # update_record.save()
            print("anything",update_record)
        return redirect(request.path_info)

class OverviewView(LoginRequiredMixin,TemplateView) :
    template_name = "manager_overview.html"
    login_url = '/login/'


class LogoutView(TemplateView) :
    def get(self, request):
        logout(request)
        return redirect('apps.attendance:home')


class LeaveRequestView(LoginRequiredMixin,TemplateView):
    template_name = "leave_requests.html"
    login_url = '/login/'

    def get_context_data(self, **kwargs: Any):
        members = list(Employee.objects.filter(manager=self.request.user).values('user_id'))
        if not members:
            pass
        requests = []
        for i in members:
            for j in list(LeaveRequest.objects.values()) :
                if i['user_id'] == j['employee_id'] :
                    j['name'] = str(User.objects.get(pk=j['employee_id']))
                    requests.append(j)
        print(requests)
        # requests = [
        #     {
        #         "id": 2,
        #         "dtm_created": datetime.datetime(
        #             2024, 6, 27, 8, 0, 3, 396264, tzinfo=datetime.timezone.utc
        #         ),
        #         "dtm_updated": datetime.datetime(
        #             2024,
        #             6,
        #             28,
        #             7,
        #             10,
        #             43,
        #             208677,
        #             tzinfo=datetime.timezone.utc,
        #         ),
        #         "employee_id": 3,
        #         "leave_type": "EARNED",
        #         "start_date": datetime.date(2024, 6, 18),
        #         "end_date": datetime.date(2024, 6, 27),
        #         "is_approved": True,
        #         "name": "Employee1",
        #     },
        #     {
        #         "id": 1,
        #         "dtm_created": datetime.datetime(
        #             2024, 6, 27, 7, 58, 6, 770908, tzinfo=datetime.timezone.utc
        #         ),
        #         "dtm_updated": datetime.datetime(
        #             2024, 6, 27, 7, 58, 6, 770927, tzinfo=datetime.timezone.utc
        #         ),
        #         "employee_id": 4,
        #         "leave_type": "LOP",
        #         "start_date": datetime.date(2024, 6, 27),
        #         "end_date": datetime.date(2024, 6, 29),
        #         "is_approved": None,
        #         "name": "Employee2",
        #     },
        # ]
        return {"data": requests[::-1]}


# def leave_data(request):
#     if request.method == "POST" :
#         print("------------")
#         print("data",request.__dict__)
#         print("------------")
#         return redirect('attendance:leaveRequest')


class LeaveRequestAPIView(ListView):
    queryset = LeaveRequest.objects.all()
    template_name = "leave_requests.html"

    def render_to_response(self, context):
        # print("------------------")
        # print(str(self.request.user))
        # print("------------------")
        data = list(context["object_list"].values())
        data.append({"user": str(self.request.user)})
        return JsonResponse(data, safe=False)


def requestLeave(request):
    if request.method == "GET":
        data = list(LeaveRequest.objects.values())
        # print("data",request.__dict__)
        return JsonResponse(data, safe=False)


@require_POST
def approve_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.is_approved = True
    leave_request.save()
    return redirect("apps.attendance:leaveRequest")


@require_POST
def reject_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.is_approved = False
    leave_request.save()
    return redirect("apps.attendance:leaveRequest")
