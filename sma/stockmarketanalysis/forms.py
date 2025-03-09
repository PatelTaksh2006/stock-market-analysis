from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django.core.exceptions import ValidationError

# from django.contrib.auth import commit
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    CHOICE_ROLE=[
        ('investor','investor'),
        ('guider','guider'),
        ('manager','manager'),
    ]

    role=forms.ChoiceField(label="Login as",choices=CHOICE_ROLE,widget=forms.Select,error_messages={'required': ''})
    
    

    password = forms.CharField(widget=forms.PasswordInput(),label="Password")
    # # RememberMe=forms.BooleanField(label="Remeber me",error_messages={'required': '\n'})


class SignUpForm(UserCreationForm):
    # email = forms.EmailField(required=True)
    
    ROLE_CHOICES = [
        ('investor', 'Investor'),
        ('guider', 'Guider'),
        ('manager','manager'),
    ]
    
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Register as")
    name = forms.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = ("role", "username", "email", "password1", "password2")
    field_order = ["name", "role", "username", "email", "password1", "password2"]
    def save(self, commit=True):
        user = super().save(commit=False)
        # user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']

        # Modify username only in backend for Guiders
        if commit:
            user.save()
        return user
    

class searchForm(forms.Form):
    name=forms.CharField(label="search stock",widget=forms.TextInput(attrs={'placeholder':'Search for stocks...'}))


class InvestmentForm(forms.Form):
    investment = forms.IntegerField(
        label="Monthly Investment Amount (₹)",
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 5000'})
    )
    
    duration = forms.IntegerField(
        label="Investment Duration (Years)",
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 5'})
    )
    
    expected_return = forms.FloatField(
        label="Expected Rate of Return (% per annum)",
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 12'})
    )
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'placeholder': 'Your Feedback', 'rows': 4})
        }
class ConsultationForm(forms.ModelForm):
    prefered_date=forms.DateField(widget=forms.DateInput(attrs={"type":"date"}),required=True)
    class Meta:
        model=investorConsultation
        fields=("goal","prefered_date","info")

    

class WebinarForm(forms.Form):
    data=Webinar.objects.filter(isApproved=True)
    web=forms.MultipleChoiceField(choices=data,widget=forms.CheckboxSelectMultiple,required=True,label="Select a Webinar:")


class PaperTradingStock(forms.ModelForm):
    stock_name=forms.CharField(required=True)
    no_of_purchase=forms.IntegerField(label="Quantity",required=True)
    choice=[
        ('select','select'),
        ('buy','Buy'),
        ('sell','Sell')
    ]
    buy_sell=forms.ChoiceField(label="Buy or Sell",choices=choice,widget=forms.Select)
    # stock_name=forms.CharField(label="Stock",required=True)
    class Meta:
        model=InvestorStock
        fields=["stock_name","no_of_purchase","buy_sell"]

    
# class PaymentForm(forms.Form):
#     card_number = forms.CharField(
#         max_length=16, 
#         min_length=16,  # Ensure exactly 16 digits
#         label="Card Number",
#         required=True,
#         validators=[validate_card_number],  # Apply custom validation
#         widget=forms.NumberInput(attrs={"placeholder": "1234567890123456", "pattern": "[0-9]{16}"})
#     )
#     expiry_date = forms.DateField(
#         label="Expiry Date (MM/YYYY)",
#         widget=forms.DateInput(attrs={'type': 'month'}),
#         input_formats=['%Y-%m'],  # Adjust input format
#         required=True
#     )
#     cvv = forms.CharField(
#         max_length=3, 
#         min_length=3,  # Ensure exactly 3 digits
#         required=True, 
#         widget=forms.PasswordInput(attrs={"placeholder": "***", "pattern": "[0-9]{3}"})
#     )



class specialityForm(forms.ModelForm):
    SPECIALTY_CHOICES = [
        ('Retirement Planning', 'Retirement Planning'),
        ('Wealth Building', 'Wealth Building'),
        ('Tax Saving', 'Tax Saving'),
        ('Education Fund', 'Education Fund')
    ]

    experties = forms.ChoiceField(choices=SPECIALTY_CHOICES, widget=forms.Select, required=True)

    class Meta:
        model = Guider
        fields = ['experties']


class WebinarRegisterForm(forms.ModelForm):
    class Meta:
        model=Webinar
        fields=["title","date","time","duration","link"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),  
            "time": forms.TimeInput(attrs={"type": "time"}), 
            "duration":forms.NumberInput(attrs={"min": 30}), 
            "link": forms.URLInput(attrs={"placeholder": "https://meet.google.com/topic"}),
        }

    