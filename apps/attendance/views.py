from typing import Any
from django.shortcuts import redirect, render , HttpResponse , get_object_or_404
from django.views.generic import TemplateView , View , ListView
from .models import LeaveRequest
from django.http import JsonResponse
# Create your views here.


class LeaveRequestView(TemplateView) :
    template_name = 'leave_requests.html'

    def get_context_data(self, **kwargs: Any):
        return {}


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
        print("------------------")
        print(str(self.request.user))
        print("------------------")
        data = list(context['object_list'].values())
        data.append({"user":str(self.request.user)})
        return JsonResponse(data, safe=False)


def requestLeave(request) :
    if request.method == "GET" :
        data = list(LeaveRequest.objects.values())
        # print("data",request.__dict__)
        return JsonResponse(data,safe=False)