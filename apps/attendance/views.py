from typing import Any
from urllib import request
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, ListView
from apps import attendance
from project.settings.settings import LOGOUT_URL
from .models import Employee, LeaveRequest , Attendance , Status
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
import datetime , calendar
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
import json
from django.core.exceptions import ObjectDoesNotExist
from dateutil.relativedelta import relativedelta

# Create your views here.


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = "/login/"

    def get_context_data(self):
        today = datetime.datetime.now()
        late_comers = []
        absent = []
        if self.request.user.is_superuser:
            total_employees = Employee.objects.all()
            p=a=s=l=0
            for employee in Attendance.objects.filter(fordate=today) :
                if str(employee.status) == "Present":
                    p += 1
                elif str(employee.status) == "Late" :
                    late_comers.append(employee)
                    l += 1
                elif str(employee.status) == "Sick":
                    s += 1
                    absent.append(employee)
                else:
                    a += 1
                    absent.append(employee)
            members = list(Employee.objects.values('user_id'))
            if not members:
                pass
            requests = []
            for i in members:
                for j in list(LeaveRequest.objects.values()) :
                    if i['user_id'] == j['employee_id'] :
                        j['name'] = str(User.objects.get(pk=j['employee_id']))
                        requests.append(j)
        else:
            total_employees = Employee.objects.filter(manager=self.request.user)
            p=a=s=l=0
            # For present day
            employees = [i for i in Attendance.objects.filter(fordate=today) if Employee.objects.get(user=i.employee).manager == self.request.user]
            for employee in employees:
                if str(employee.status) == "Present":
                    p += 1
                elif str(employee.status) == "Late" :
                    late_comers.append(employee)
                    l += 1
                elif str(employee.status) == "Sick":
                    s += 1
                    absent.append(employee)
                else:
                    a += 1
                    absent.append(employee)
            # print("b",Employee.objects.get(user=b[0].employee).manager)
            members = list(Employee.objects.filter(manager=self.request.user).values('user_id'))
            if not members:
                pass
            requests = []
            for i in members:
                for j in list(LeaveRequest.objects.values()) :
                    if i['user_id'] == j['employee_id'] :
                        j['name'] = str(User.objects.get(pk=j['employee_id']))
                        requests.append(j)
        return {"weekday":today.strftime("%A"),"date":today.strftime("%d/%m/%Y"),"requests":requests[::-1],"present":p,"abs":a,"late":l,"sick":s,"all_employees":total_employees,"late_comers":late_comers,"absent":absent,"is_manager":self.request.user.is_staff,"is_admin":self.request.user.is_superuser}


class MarkAttendanceView(LoginRequiredMixin,TemplateView) :
    template_name = "mark_attendance.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        members = Employee.objects.filter(manager=self.request.user)
        status = Status.objects.all()
        attendance_records = Attendance.objects.filter(employee__in=members.values('user'))
        context = {"status_options":status,"records":attendance_records,"date":datetime.datetime.strftime(datetime.datetime.today(),"%Y-%m-%d"),"employees":members,"is_manager":True,"is_admin":self.request.user.is_superuser}
        return context

    def post(self,request):
        '''
        Method to post data into database
        '''
        attendance_date,records = request.POST.get("attendance_date"),json.loads(request.POST.get("records"))
        for record in records:
            remark = record['remark'] if record['remark'] != "" else str(record['status'])
            user = User.objects.get(username=record['user'])
            status = Status.objects.get(status=record['status'])
            try:
                existing_record = Attendance.objects.filter(employee=user).get(fordate=attendance_date)
                print("existing",existing_record.status)
                existing_record.status = status
                existing_record.remarks = remark
                existing_record.save()
            except ObjectDoesNotExist:
                new_record = Attendance.objects.create(employee=user,fordate=attendance_date,status=status,remarks=remark)
                new_record.save()
            # update_record,created = Attendance.objects.update_or_create(fordate=attendance_date,employee=user,status=status,remarks=remark)
            # update_record.save()
            # print("anything",update_record)
        return redirect(request.path_info)


class OverviewView(LoginRequiredMixin,TemplateView) :
    template_name = "manager_overview.html"
    login_url = '/login/'

    def post(self,request,*args,**kwargs) :
        today = datetime.datetime.today()
        overview = []
        month,year = int(request.POST.get('month')),int(request.POST.get('year'))
        if self.request.user.is_superuser :
            employees = Employee.objects.all()
        else:
            employees = Employee.objects.filter(manager=self.request.user)
        # print(Attendance.objects.filter(employee=employees[0].user).filter(fordate=today.month))
        for employee in employees:
            employee_records = []
            current_date = datetime.datetime(year,month,1)
            end_date = datetime.datetime(year,month,calendar.monthrange(year,month)[1])
            delta = datetime.timedelta(days=1)

            while current_date <= end_date :
                if Attendance.objects.filter(fordate=current_date).filter(employee=employee.user).exists() :
                    record = Attendance.objects.filter(fordate=current_date).filter(employee=employee.user)
                    employee_records.append({"date":record[0].fordate,"status":record[0].status.status})
                else :
                    employee_records.append({"date":current_date,"status":"Unknown"})
                current_date += delta
            overview.append({employee.user.username:employee_records})

            # for record in Attendance.objects.filter(employee=employee.user) :
            #     if record.fordate.month == month and record.fordate.year == year :
            #         employee_records.append({"date":record.fordate,"status":record.status.status})
            # overview.append({employee.user.username:employee_records})
        context = {"overview":overview}
        print(json.dumps(overview,indent=6,default=str))
        return JsonResponse(overview,safe=False)


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
        return {"data": requests[::-1]}

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
    emp = Employee.objects.get(user=leave_request.employee)
    if leave_request.leave_type == "EARNED" :
        emp.earned_leave -= 1
    elif leave_request.leave_type == "SICK" :
        emp.sick_leave -= 1
    emp.save()
    leave_request.is_approved = True
    leave_request.save()
    return redirect("apps.attendance:leaveRequest")


@require_POST
def reject_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.is_approved = False
    leave_request.save()
    return redirect("apps.attendance:leaveRequest")
