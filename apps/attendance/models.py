from django.db import models
from django.contrib.auth.models import User
from qux.models import QuxModel
from qux.utils.date import eomonth,fomonth

# Create your models here.
class Employee(QuxModel):
    user = models.OneToOneField(User, related_name="employee",on_delete=models.CASCADE)
    manager = models.ForeignKey(User,related_name="manager",on_delete=models.CASCADE)
    earned_leave = models.IntegerField(default=15)
    sick_leave = models.IntegerField(default=9)
    
    
    def calc_monthly_lop(self, fordate):
        start = fomonth(fordate, 0)
        end = eomonth(fordate, 0)
        # find records between start and end
        # calculate by record and aggregate
        # return results
        return 0
    
    
    def leave_summary(self):
        """
        [
            {
                "period": datetime.date(y, m, 1),
                "opening_earned_leave": 123,
                "days_on_leave": [list of dates on leave],
                "opening_sick_leave": 123,
                "sick_days": [list of sick days],
                "lop": 32
            },
            {...}
        ]
        """
        return
    
    def __str__(self):
        return str(self.user)


class Status(QuxModel):
    """
    ["present", "vacation", "sick", "late", "unknown"]
    """
    status = models.CharField(max_length=16, unique=True)
    is_earned_leave = models.BooleanField(default=False)
    is_sick_leave = models.BooleanField(default=False)
    
    
    def __str__(self):
        return str(self.status)



class Attendance(QuxModel):
    employee = models.ForeignKey(User,on_delete=models.CASCADE)
    fordate = models.DateField()
    status = models.ForeignKey(Status,on_delete=models.CASCADE)
    remarks = models.TextField()
    
    @property
    def is_earned_leave(self):
        return self.status._is_earned_leave
    
    @property
    def is_sick_leave(self):
        return self.status.is_sick_leave
    
    @property
    def lop_days(self):
        return self._lop_days
    
    def __str__(self):
        return str(self.employee) + "_" + str(self.fordate)


LeaveTypes = (
    ("EARNED", "Earned"),
    ("SICK", "Sick"),
    ("LOP", "Unpaid"),
    )

class LeaveRequest(QuxModel):
    employee = models.ForeignKey(User,on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=16, choices=LeaveTypes)
    start_date = models.DateField()
    end_date = models.DateField()
    is_approved = models.BooleanField(default=None, blank=True, null=True)
    
    def __str__(self):
        return str(self.employee) + " " + str(self.start_date) + " " + str(self.end_date)