from django.forms import ModelForm,DateInput,Select
from .models import LeaveRequest

class LeaveRequestForm(ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type","start_date","end_date"]
        widgets = {
            'leave_type':Select(),
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'})
        }