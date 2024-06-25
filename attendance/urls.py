from django.urls import path , include
from . import views
from django.views.generic.base import TemplateView

app_name = "attendance"

urlpatterns = [
    path("",TemplateView.as_view(template_name="manager_dash.html"),name="home"),
]