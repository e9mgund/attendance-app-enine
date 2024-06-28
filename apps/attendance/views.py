from typing import Any
from urllib import request
from django.shortcuts import redirect, render , HttpResponse , get_object_or_404
from django.views.generic import TemplateView , View , ListView
from .models import Employee, LeaveRequest
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
# Create your views here.


class LeaveRequestView(TemplateView) :
    template_name = 'leave_requests.html'

    def get_context_data(self, **kwargs: Any):
        # members = list(Employee.objects.filter(manager=self.request.user).values('user_id'))
        # if not members:
        #     pass
        # requests = []
        # for i in members:
        #     for j in list(LeaveRequest.objects.values()) :
        #         if i['user_id'] == j['employee_id'] :
        #             j['name'] = str(User.objects.get(pk=j['employee_id']))
        #             requests.append(j)
        # print(requests)
        requests = [{'id': 2, 'dtm_created': datetime.datetime(2024, 6, 27, 8, 0, 3, 396264, tzinfo=datetime.timezone.utc), 'dtm_updated': datetime.datetime(2024, 6, 28, 7, 10, 43, 208677, tzinfo=datetime.timezone.utc), 'employee_id': 3, 'leave_type': 'EARNED', 'start_date': datetime.date(2024, 6, 18), 'end_date': datetime.date(2024, 6, 27), 'is_approved': True, 'name': 'Employee1'}, {'id': 1, 'dtm_created': datetime.datetime(2024, 6, 27, 7, 58, 6, 770908, tzinfo=datetime.timezone.utc), 'dtm_updated': datetime.datetime(2024, 6, 27, 7, 58, 6, 770927, tzinfo=datetime.timezone.utc), 'employee_id': 4, 'leave_type': 'LOP', 'start_date': datetime.date(2024, 6, 27), 'end_date': datetime.date(2024, 6, 29), 'is_approved': None, 'name': 'Employee2'}]
        return {"data":requests[::-1]}


# def leave_data(request):
#     if request.method == "POST" :
#         print("------------")
#         print("data",request.__dict__)
#         print("------------")
#         return redirect('attendance:leaveRequest')

class LeaveRequestAPIView(ListView) :
    queryset = LeaveRequest.objects.all()
    template_name = 'leave_requests.html'

    def render_to_response(self, context) :
        # print("------------------")
        # print(str(self.request.user))
        # print("------------------")
        data = list(context['object_list'].values())
        data.append({"user":str(self.request.user)})
        return JsonResponse(data, safe=False)


def requestLeave(request) :
    if request.method == "GET" :
        data = list(LeaveRequest.objects.values())
        # print("data",request.__dict__)
        return JsonResponse(data,safe=False)
    

@require_POST
def approve_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.is_approved = True
    leave_request.save()
    return redirect('apps.attendance:requests')

@require_POST
def reject_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.is_approved = False
    leave_request.save()
    return redirect('apps.attendance:requests')