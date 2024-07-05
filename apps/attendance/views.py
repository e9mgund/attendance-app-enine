from typing import Any
import json
import datetime
import calendar
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Employee, LeaveRequest, Attendance, Status
from .forms import LeaveRequestForm

# Create your views here.


class EmployeeDashboard(LoginRequiredMixin, TemplateView):
    """
    To handle employee dashboard
    """

    template_name = "employee_dashboard.html"
    login_url = "/login/"

    def calculate_leaves(self):
        """
        Calculates monthly leaves status
        """
        approved_requests = LeaveRequest.objects.filter(
            employee=self.request.user
        ).filter(is_approved=True)
        sick_requests = approved_requests.filter(leave_type="SICK")
        earned_requests = approved_requests.filter(leave_type="EARNED")
        unpaid_requests = approved_requests.filter(leave_type="LOP")
        unpaid = sum(
            [
                (record.end_date - record.start_date).days + 1
                for record in unpaid_requests
            ]
        )
        return unpaid

    # def get(self,request) :
    #     if self.request.user.is_superuser :
    #         return redirect('apps.attendance:managerdash')
    def get_context_data(self, **kwargs):
        user = self.request.user
        if not user.is_superuser :
            is_manager = user.manager.exists()
            employee = Employee.objects.get(user=user)
            sick, earned, unpaid = (
                employee.sick_leave,
                employee.earned_leave,
                self.calculate_leaves(),
            )
            print("--------------------------------------------------------------")
            print("SICK,EARNED,UNPAID:", sick, earned, unpaid)
            print("--------------------------------------------------------------")
            # if earned==15:
            #     unpaid += earned - 15
            #     earned = 15
            # # else:
            #     earned = 15- earned
            # if sick>9:
            #     unpaid += sick - 9
            #     sick = 0
            # else:
            #     sick = 9 - sick

            leave_requests = LeaveRequest.objects.filter(
                employee=self.request.user
            ).order_by("-start_date")
            context = {
                "form": LeaveRequestForm,
                "leave_requests": leave_requests,
                "num_requests": len(leave_requests) != 0,
                "employee_records": Attendance.objects.filter(
                    employee=user
                ).order_by("-fordate"),
                "is_manager": is_manager,
                "is_admin": user.is_superuser,
                "sick": sick,
                "earned": earned,
                "unpaid": abs(unpaid),
                "user": str(user).capitalize(),
            }
        else:
            context = {"is_manager":user.is_staff,"is_admin":user.is_superuser,"user":str(user).capitalize()}
        return context

    def post(self, request):
        leave_type, start_date, end_date = (
            request.POST.get("leave_type"),
            request.POST.get("start_date"),
            request.POST.get("end_date"),
        )
        new_request = LeaveRequest.objects.create(
            employee=self.request.user,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            is_approved=None,
        )
        new_request.save()
        return redirect(request.path_info)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = "/login/"

    def get_context_data(self):
        # if not self.request.user.is_superuser or not self.request.user.is_staff :
        #     return redirect('apps.attendance:emp_dash')
        today = datetime.datetime.now()
        late_comers = []
        absent = []
        if self.request.user.is_superuser:
            total_employees = Employee.objects.all()
            p = a = s = l = 0
            for employee in Attendance.objects.filter(fordate=today):
                if str(employee.status) == "Present":
                    p += 1
                elif str(employee.status) == "Late":
                    late_comers.append(employee)
                    l += 1
                elif str(employee.status) == "Sick":
                    s += 1
                    absent.append(employee)
                else:
                    a += 1
                    absent.append(employee)
            members = list(Employee.objects.values("user_id"))
            if not members:
                pass
            requests = []
            for i in members:
                for j in list(LeaveRequest.objects.values()):
                    if i["user_id"] == j["employee_id"]:
                        j["name"] = str(User.objects.get(pk=j["employee_id"]))
                        requests.append(j)
        else:
            total_employees = Employee.objects.filter(
                manager=self.request.user
            )
            p = a = s = l = 0
            # For present day
            employees = [
                i
                for i in Attendance.objects.filter(fordate=today)
                if Employee.objects.get(user=i.employee).manager
                == self.request.user
            ]
            for employee in employees:
                if str(employee.status) == "Present":
                    p += 1
                elif str(employee.status) == "Late":
                    late_comers.append(employee)
                    l += 1
                elif str(employee.status) == "Sick":
                    s += 1
                    absent.append(employee)
                else:
                    a += 1
                    absent.append(employee)
            # print("b",Employee.objects.get(user=b[0].employee).manager)
            members = list(
                Employee.objects.filter(manager=self.request.user).values(
                    "user_id"
                )
            )
            if not members:
                pass
            requests = []
            for i in members:
                for j in list(LeaveRequest.objects.values()):
                    if i["user_id"] == j["employee_id"]:
                        j["name"] = str(User.objects.get(pk=j["employee_id"]))
                        requests.append(j)
        return {
            "weekday": today.strftime("%A"),
            "date": today.strftime("%d/%m/%Y"),
            "requests": requests,
            "present": p,
            "abs": a,
            "late": l,
            "sick": s,
            "all_employees": total_employees,
            "late_comers": late_comers,
            "absent": absent,
            "is_manager": self.request.user.is_staff,
            "is_admin": self.request.user.is_superuser,
        }


class MarkAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = "mark_attendance.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser:
            members = Employee.objects.all()
        else:
            members = Employee.objects.filter(manager=self.request.user)
        status = Status.objects.all()
        attendance_records = Attendance.objects.filter(
            employee__in=members.values("user")
        )
        print("attendance", attendance_records)
        context = {
            "status_options": status,
            "records": attendance_records,
            "date": datetime.datetime.strftime(
                datetime.datetime.today(), "%Y-%m-%d"
            ),
            "employees": members,
            "is_manager": True,
            "is_admin": self.request.user.is_superuser,
        }
        return context

    def post(self, request):
        """
        Method to post data into database
        """
        attendance_date, records = request.POST.get(
            "attendance_date"
        ), json.loads(request.POST.get("records"))
        for record in records:
            remark = (
                record["remark"]
                if record["remark"] != ""
                else str(record["status"])
            )
            user = User.objects.get(username=record["user"])
            status = Status.objects.get(status=record["status"])
            try:
                existing_record = Attendance.objects.filter(employee=user).get(
                    fordate=attendance_date
                )
                print("existing", existing_record.status)
                existing_record.status = status
                existing_record.remarks = remark
                existing_record.save()
            except ObjectDoesNotExist:
                new_record = Attendance.objects.create(
                    employee=user,
                    fordate=attendance_date,
                    status=status,
                    remarks=remark,
                )
                new_record.save()
        return redirect(request.path_info)


class OverviewView(LoginRequiredMixin, TemplateView):
    template_name = "manager_overview.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs: Any):
        context = {
            "is_manager": self.request.user.is_staff,
            "is_admin": self.request.user.is_superuser,
        }
        return context

    def post(self, request, *args, **kwargs):
        today = datetime.datetime.today()
        overview = []
        month, year = int(request.POST.get("month")), int(
            request.POST.get("year")
        )
        if self.request.user.is_superuser:
            employees = Employee.objects.all()
        else:
            employees = Employee.objects.filter(manager=self.request.user)
        for employee in employees:
            employee_records = []
            current_date = datetime.datetime(year, month, 1)
            end_date = datetime.datetime(
                year, month, calendar.monthrange(year, month)[1]
            )
            delta = datetime.timedelta(days=1)

            while current_date <= end_date:
                if (
                    Attendance.objects.filter(fordate=current_date)
                    .filter(employee=employee.user)
                    .exists()
                ):
                    record = Attendance.objects.filter(
                        fordate=current_date
                    ).filter(employee=employee.user)
                    employee_records.append(
                        {
                            "date": record[0].fordate,
                            "status": record[0].status.status,
                        }
                    )
                else:
                    employee_records.append(
                        {"date": current_date, "status": "Unknown"}
                    )
                current_date += delta
            overview.append({employee.user.username: employee_records})
        context = {"overview": overview}
        return JsonResponse(overview, safe=False)


class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return redirect("apps.attendance:emp_dash")


class LeaveRequestView(LoginRequiredMixin, TemplateView):
    template_name = "leave_requests.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs: Any):
        if self.request.user.is_superuser:
            members = list(Employee.objects.all().values("user_id"))
        else:
            members = list(
                Employee.objects.filter(manager=self.request.user).values(
                    "user_id"
                )
            )
        requests = []
        for i in members:
            for j in list(LeaveRequest.objects.values()):
                if i["user_id"] == j["employee_id"]:
                    j["name"] = str(User.objects.get(pk=j["employee_id"]))
                    requests.append(j)
        print(requests)
        return {
            "data": requests,
            "is_manager": self.request.user.is_staff,
            "is_admin": self.request.user.is_superuser,
        }


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
    if leave_request.leave_type == "EARNED":
        emp.earned_leave -= 1
    elif leave_request.leave_type == "SICK":
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
