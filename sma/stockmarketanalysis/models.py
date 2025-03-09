from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('investor', 'Investor'),
        ('guider', 'Guider'),
        ('manager','manager')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="investor")
    feedback=models.CharField(max_length=100,null=True,blank=True)

class Investor(models.Model):
    # id=models.CharField(max_length=8)
    user=models.ForeignKey(CustomUser,unique=True,on_delete=models.CASCADE)
    name=models.CharField(max_length=20,null=True,blank=True)
    email=models.EmailField()
    # password=models.CharField(max_length=15)
    mobile_no=models.IntegerField(null=True,blank=True)
    investedAmount=models.IntegerField(null=True,blank=True)
    payementDate=models.DateField(null=True,blank=True)
    ispaid=models.BooleanField(default=False)



class Manager(models.Model):
    user=models.ForeignKey(CustomUser,unique=True,on_delete=models.CASCADE)
    name=models.CharField(max_length=30,null=True,blank=True)
    email=models.EmailField()
    # password=models.CharField(max_length=15)
    mobile_no=models.BigIntegerField(max_length=10,null=True,blank=True)




class Guider(models.Model):
    # id=models.CharField(max_length=8)
    user=models.ForeignKey(CustomUser,unique=True,on_delete=models.CASCADE)
    name=models.CharField(max_length=30)
    email=models.EmailField()
    # password=models.CharField(max_length=15)
    # mobile_no=models.IntegerField(null=True,blank=True)
    experties=models.CharField(max_length=50,null=True,blank=True)
    isSelected=models.BooleanField(default=False)



class Stock(models.Model):
    # symbol=models.CharField()
    name=models.CharField(max_length=40)
    current_price=models.FloatField()
    volume=models.IntegerField()
    sector=models.CharField(max_length=30)
    
class InvestorStock(models.Model):
    investor=models.ForeignKey(Investor,on_delete=models.CASCADE)
    stock=models.ForeignKey(Stock,on_delete=models.CASCADE)
    no_of_purchase=models.IntegerField(null=True,blank=True)
    price_of_buy=models.FloatField(null=True,blank=True)



class Watchlist(models.Model):
    investor=models.ForeignKey(Investor,on_delete=models.CASCADE)
    stock=models.ForeignKey(Stock,on_delete=models.CASCADE)


class Webinar(models.Model):
    guider=models.ForeignKey(Guider,on_delete=models.CASCADE)
    title=models.CharField(max_length=20)
    date=models.DateField(null=True,blank=True)
    time=models.TimeField(null=True,blank=True)
    link=models.CharField(max_length=60,default="")
    duration=models.IntegerField()
    number_of_attendee=models.IntegerField(default=0)
    isApproved=models.BooleanField(default=False)


class UserWebinar(models.Model):
    investor=models.ForeignKey(Investor,on_delete=models.CASCADE)
    webinar=models.ForeignKey(Webinar,on_delete=models.CASCADE)


class investorConsultation(models.Model):
    goal_choices=[
        ('Retirement Planning','Retirement Planning'),
        ('Wealth Building','Wealth Building'),
        ('Tax Saving','Tax Saving'),
        ('Education Fund','Education Fund')
    ]
    user=models.ForeignKey(Investor,on_delete=models.CASCADE)
    goal=models.CharField(max_length=20,choices=goal_choices,default="Wealth Building")
    prefered_date=models.DateField()
    info=models.CharField(max_length=60)
