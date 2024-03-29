﻿from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Employees(models.Model): #Summary: Table in PSQL database containing employees
    
    # Static methods required by django for uploading files/documents to custom directory
    # Declared inside scope of this class for legibility
    
    def photoToUserDir(instance, file: str):
        return f'media/{instance.user.id}_{instance.user.username}/{file}'
    def onboard_docsToUserDir(instance, file: str):
        return f'media/{instance.user.id}_{instance.user.username}/{file}'
        
    # Instantiated methods to be used in views/API. For validation or other utilities

    def photoToUrl(self):
        try:
            url=str(self.photo.url)
        except:
            url=None
        return url
    def validatephotoSize(self,value):
        filesize= value.size
        max_size = 100000000.0
        if filesize > max_size:
            raise ValidationError(f"The maximum size of uploading to photo is {max_size/10**6} mb.")
        else:
            return value
    def onboard_docsToUrl(self):
        try:
            url=str(self.onboard_docs.url)
        except:
            url=None
        return url
    def validateonboard_docsSize(self,value):
        filesize= value.size
        max_size = 100000000.0
        if filesize > max_size:
            raise ValidationError(f"The maximum size of uploading to onboard_docs is {max_size/10**6} mb.")
        else:
            return value
            
    #id = models.IntegerField(null=False, blank=False, default=0, primary_key = True)
    # This field is not necessary since Django autocreates id field in PSQL database

    name = models.TextField(max_length=50)
    work_email = models.TextField(max_length=50, null=True, blank=True, default='')
    department = models.TextField(max_length=50, null=True, blank=True, default='')
    job_title = models.TextField(max_length=50, null=True, blank=True, default='')
    hourly = models.BooleanField(default=True)
    pay_rate = models.DecimalField(null=True, blank=True, default=None, max_digits=10,decimal_places=2)
    start_date = models.DateTimeField(null=True, blank=True)
    photo = models.ImageField(null=True, blank=True, upload_to= photoToUserDir) #custom uploaded to media folder. Filesize validation will be called on view
    onboard_docs = models.FileField(null=True, blank=True, upload_to= onboard_docsToUserDir) #custom uploaded to media folder. Filesize validation will be called on view
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        app_label = 'app_payroll'
    def __str__(self):
        return f"{self.id}-{self.name}"
        


class TimeSheet(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, blank=True, null=True )
    description = models.TextField(max_length=2000, null=True, blank=True)
    bill_rate = models.DecimalField(default = 0, max_digits=10,decimal_places=2)
    total_time = models.DecimalField(default = 0, max_digits=10,decimal_places=2)
    total_bill = models.DecimalField(default = 0, max_digits=20,decimal_places=2)
    date = models.DateTimeField()
    date_added = models.DateTimeField(auto_now_add=True, auto_now=False) 
    date_modified = models.DateTimeField(auto_now=True) 

    def getTotalMinutes(self) -> float:
        lineitems=self.lineitems_set.all()
        total= sum([item.num_minutes for item in lineitems])
        return total
        
    def getEmployee(self) -> str:
        if self.employee == None:
            return "Unassigned Employee"
        return self.employee.name
        
    class Meta:
        verbose_name = 'TimeSheet'
        verbose_name_plural = 'TimeSheet'
        app_label = 'app_payroll'
    def __str__(self):
        return f"{self.id}-{self.getEmployee()}"
        
class LineItems(models.Model):
    timesheet = models.ForeignKey(TimeSheet, on_delete=models.CASCADE, blank=True, null=True )
    num_minutes=models.DecimalField(default=0, max_digits=8,decimal_places=2) 
    memo = models.TextField(max_length=100, null=True, blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True, auto_now=False) 
    date_modified = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return str(self.id)
    class Meta:
        verbose_name = 'LineItems'
        verbose_name_plural = 'LineItems'
        app_label = 'app_payroll'
        
class WorkSchedule(models.Model):

    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, blank=True, null=True )
    start_diff = models.DecimalField(null=True, blank=True, default=None, max_digits=4,decimal_places=2) #in minutes
    end_diff = models.DecimalField(null=True, blank=True, default=None, max_digits=4,decimal_places=2) #in minutes
    clock_in = models.DateTimeField(auto_now_add=True, auto_now=False) #automatically added on POST, remaining times will be updated on PUT
    lunch_in = models.DateTimeField()
    lunch_out = models.DateTimeField()
    clockout = models.DateTimeField()

    def validatelateLength(self, length: int = 10):
        if len(str(self.late)) > length:
            return False
        else:
            return True
    class Meta:
        verbose_name = 'EmpTimeSheet'
        verbose_name_plural = 'EmpTimeSheet'
        app_label = 'app_payroll'

