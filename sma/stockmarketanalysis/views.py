from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login ,logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from datetime import date
from .forms import *
from django.db.models import Q
# Create your views here.
def home(request):
    return render(request,'home.html')

def logout_request(request):
    logout(request)
    return redirect("/")

# def paperTrading(request):
#     return render(request,'paperTrading.html')
def feedback_page(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST or None, instance=request.user)
        if form.is_valid():
            form.save()
            if request.user.role=="investor":
                return redirect("user_dashboard")
            elif request.user.role=="guider":
                return redirect("guider_dashboard")
    else:
        form = FeedbackForm(instance=request.user)
        return render(request, 'feedback.html', {'form': form})

def login_page(request):
    if request.method=="POST":
        # print("in post of login")
        form=LoginForm(request, data=request.POST)
        if form.is_valid():
            # remeberme=bool(request.POST["RememberMe"])
            # if remeberme:
            # print("form is valid")
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            role = form.cleaned_data["role"]
            user=authenticate(request,username=username,password=password,role=role)
            if user is not None:
                
                # request.SESSION['role']=user.role
                if user.role == role:
                    login(request,user)
                    if user.role=="investor":
                        investor=Investor.objects.get(user=user)
                        request.session["id"]=investor.id
                        return render(request,"user_dashboard.html",{"name":investor.name})
                    elif user.role=="guider":
                        guider=Guider.objects.get(user=user)
                        request.session["id"]=guider.id
                        return redirect("guider_dashboard")
                    else:
                        return render(request,"manager_dashboard.html",{"name":"John doe"})    
                else:
                    messages.error(request,"No such user found. Please try again.")
                    return render(request,"login.html",{"form":form})
            else:
                # print("sacho user nakh")
                return render(request,"login.html",{"form":form})
        else:
            # print("form j valid nathi")
            return render(request,"login.html",{"form":form})
            

    else:
        # print("Login kar")
        form=LoginForm()
        return render(request,"login.html",{"form":form})
                            

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username=form.cleaned_data['username']
            name=form.cleaned_data["name"]
            # Prevent Investors from starting with a number
            # name=form.cleaned_data["name"]

            user.save()

            # Store Guider username for display (without "1" prefix)

            # Create corresponding entry in Investor or Guider
            if user.role == "investor":
                Investor.objects.create(name=name, email=user.email,user=user)
            elif user.role=="guider":
                Guider.objects.create(name=name, email=user.email,user=user)
            else:
                Manager.objects.create(name=name,email=user.email,user=user)
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")

        else:
            messages.error(request, "Please correct the errors in the form.")
            return render(request,"signup.html",{"form":form})

    else:
        form = SignUpForm()
        return render(request,"signup.html",{"form":form})


def userdashboard(request):
    return render(request,"user_dashboard.html")



def cms(request):
    user_id=request.session["id"]
    investor=Investor.objects.get(id=user_id)
    user_watchlist=Watchlist.objects.filter(investor=investor)
    watchlist_data=[]
    for wd in user_watchlist:
        watchlist_data.append({
            'name':wd.stock.name,
            'price':wd.stock.current_price,
            'sector':wd.stock.sector
        })
    error=None
    if request.method=="GET":
        # print(error)
        form=searchForm()
        return render(request,"current_market_state.html",{"form":form,"watchlist":watchlist_data,"error":error})
    else:
        form=searchForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]

            stock = Stock.objects.filter(name=name).first()  # Avoids raising 404 error
            if stock is None:
                error="No such Stock found"
                return render(request,"current_market_state.html",{"data":stock,"form":form,"watchlist":watchlist_data,"error":error})

            return render(request,"current_market_state.html",{"data":stock,"form":form,"watchlist":watchlist_data})

def addToWatchlist(request,name):
    investor_id=request.session["id"]
    investor=Investor.objects.get(id=investor_id)
    stock=Stock.objects.get(name=name)
    try:
        wl=Watchlist.objects.get(investor=investor,stock=stock)
    except Watchlist.DoesNotExist:
        Watchlist.objects.create(investor=investor,stock=stock)
    form=searchForm()
    return redirect("current_market_state")



from django.shortcuts import redirect
from django.urls import reverse

def papertrading(request):
    inv = Investor.objects.get(id=request.session["id"])
    user_stock = InvestorStock.objects.filter(investor=inv)
    stock_data = []

    for investor_stock in user_stock:
        stock_data.append({
            'stock_name': investor_stock.stock.name,
            'stock_quantity': investor_stock.no_of_purchase,
            'price': investor_stock.price_of_buy,
            'current_price': investor_stock.stock.current_price
        })

    if request.method == "GET":
        form = PaperTradingStock()
        error = request.GET.get("error", "")
        print(error)
        success = request.GET.get("success", "")
        print(success)
        return render(request, "paper_trading.html", {"form": form, "data": stock_data, "error": error, "success": success})

    else:
        form = PaperTradingStock(request.POST)
        if form.is_valid():
            buy_sell = form.cleaned_data["buy_sell"]
            stock_name = form.cleaned_data["stock_name"]
            quantity = form.cleaned_data["no_of_purchase"]

            try:
                stock = Stock.objects.get(name=stock_name)
                investor = Investor.objects.get(id=request.session["id"])
            except Stock.DoesNotExist:
                return redirect(reverse("papertrading") + "?error=Stock doesn't exist")

            if buy_sell == "sell":
                try:
                    stockOfInvestor = InvestorStock.objects.get(stock=stock, investor=investor)
                except InvestorStock.DoesNotExist:
                    return redirect(reverse("papertrading") + "?error=Stock doesn't exist in your buy list")

                if quantity > stockOfInvestor.no_of_purchase:
                    return redirect(reverse("papertrading") + "?error=Please enter a valid amount of stock")

                stockOfInvestor.no_of_purchase -= quantity
                if stockOfInvestor.no_of_purchase == 0:
                    stockOfInvestor.delete()
                else:
                    stockOfInvestor.save()

                return redirect(reverse("papertrading") + "?success=Successfully sold")

            elif buy_sell == "buy":
                stockOfInvestor, created = InvestorStock.objects.get_or_create(stock=stock, investor=investor)

                if created:
                    stockOfInvestor.no_of_purchase = quantity
                    stockOfInvestor.price_of_buy = stock.current_price
                else:
                    stockOfInvestor.no_of_purchase += quantity

                stockOfInvestor.save()
                return redirect(reverse("papertrading") + "?success=Successfully bought")

            else:
                return redirect(reverse("papertrading") + "?error=Please select an appropriate option")
        else:
            return redirect(reverse("papertrading") + "?error=Invalid form submission")
   
def webinar_registration(request):
    if request.method == "GET":
        context = {"data": Webinar.objects.filter(isApproved=True)}
        registered_webinars = set()  # Store already registered webinar IDs

        for web in context["data"]:
            userWeb = UserWebinar.objects.filter(webinar=web, investor=Investor.objects.get(id=request.session["id"])).first()
            if userWeb:
                registered_webinars.add(web.id)
        error_message = request.GET.get("error", "")  # Get error message from URL if exists
        return render(request, "webinar_registration.html", {
            "register": bool(context["data"]),
            **context,
            "registered_webinars": registered_webinars,
            "error": error_message  # Pass error message to template
        })
    else:
        selected = request.POST.getlist("web")  # Get multiple selected values as a list

        if not selected:  # Validation: Check if user selected any webinar
            # error_message = urlencode({"error": f"Invalid webinar ID: {webinar_id}"})
            return redirect(reverse('webinar_registration')+"?error=For register you have to select atleast one from below")

        # Update attendee count
        for webinar_id in selected:
            try:
                webinar = Webinar.objects.get(id=webinar_id)
                webinar.number_of_attendee += 1
                webinar.save()
                UserWebinar.objects.create(investor=Investor.objects.get(id=request.session["id"]),webinar=webinar)
            except Webinar.DoesNotExist:
                return render(request, "webinar_registration.html", {
                    "register": True, 
                    "data": Webinar.objects.filter(isApproved=True), 
                    "error": f"Invalid webinar ID: {webinar_id}"
                })
        # investor=Investor.objects.get(id=request.session["id"])
        return redirect("user_dashboard")


def marketanalysis(request):
    form=searchForm()
    return render(request,"market_analy_pred.html",{"form":form})
#     if request.method=="GET":
#         form=searchForm()
#         return render(request,"market_analy_pred.html",{"form":form})
#     else:
#         form=searchForm(request.POST)
#         if form.is_valid():
#             name=form.cleaned_data["name"]
#             try:
#                 stock=Stock.objects.get(name=name)
#             except Stock.DoesNotExist:
#                 messages.error(request, "Given stock does not exist")
#                 return render(request, "market_analy_pred.html", {"form": form})
#             # if stock is None:
#             #     messages.error(request,"Given stock is not exist")
#             #     return render(request,"market_analy_pred.html",{"form":form})
#         return render(request,"market_analy_pred.html",{"form":form})
            

def sip(request):
    if request.method=="GET":
        form=InvestmentForm()
        return render(request,"sip.html",{"form":form})
    else:
        form=InvestmentForm(request.POST)
        if form.is_valid():
            investment=form.cleaned_data["investment"]
            duration=form.cleaned_data["duration"]
            expected_return=form.cleaned_data["expected_return"]
            
            investment=float(investment)
            duration=float(duration)
            expected_return=float(expected_return)

            r=expected_return/12/100
            n=duration*12
            
            future_value=investment * ((pow(1+r,n)-1)/r) * (1+r)
            return render(request,"sip.html",{"ans":'{0:.3f}'.format(future_value),"form":form})
            

def consultation(request):
    if request.method=="GET":
        form=ConsultationForm()
        return render(request,"consultation.html",{"form":form})
    else:
        form=ConsultationForm(request.POST)
        if form.is_valid():
            prefered_date=form.cleaned_data["prefered_date"]
            today = date.today()
            # print(today)  
            if(today>prefered_date):
                error="Please Enter valid date."
                return render(request,"consultation.html",{"form":form,"error":error})
            instance=form.save(commit=False)
            investor_id=request.session["id"]
            if investor_id:
                # try:
                investor = Investor.objects.get(id=investor_id)  
                instance.user = investor  
                instance.save()  
                print("success")  
                return redirect("user_dashboard")
                print("success")  
                # except Investor.DoesNotExist:
                #     return redirect("user_dashboard")
            # return render(request,"user_dashboard.html")
        else:
            error="Please correct the errors in the form."
            return render(request,"consultation.html",{"form":form,"error":error})
        
# def payment(request):
#     if request.method == "GET":
#         form = PaymentForm()
#         error = request.GET.get("error", "")  # Get error message from URL if exists
#         return render(request, "payement.html", {"form": form, "error": error})

#     else:
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             expiry_date = form.cleaned_data["expiry_date"]
#             today = date.today()

#             # Ensure expiry date is in the future
#             if expiry_date < today.replace(day=1):  # Only check year & month
#                 # error_message = urlencode({"error": "Your card date is already expired"})
#                 return redirect(reverse('payment')+"?error_message=Your card date is already expired")

#             investor = Investor.objects.get(id=request.session["id"])
#             if investor.ispaid:
#                 # error_message = urlencode({"error": "Your subscription is already active"})
#                 return redirect(reverse('payment')+"?error_message=Your subscription is already active")
#             else:
#                 investor.ispaid = True
#                 investor.save()
#                 # return redirect(f"{reverse('user_dashboard')}?{urlencode({'success': 'You are upgraded to premium membership'})}")
#                 return redirect(reverse('payment')+"?success=You are upgraded to premium membership")

#         else:
#             # error_message = urlencode({"error": "Invalid input. Please check your details."})
#             # return redirect(f"{reverse('payment')}?{error_message}")

def guiderdashboard(request):
   guider_id=request.session["id"]
   guider=Guider.objects.get(id=guider_id)
   if request.method=="GET":
       if guider.experties is None:
           print("guider has not any experties")
           form=specialityForm()
           return render(request,"guider_dashboard.html",{"form":form})
      
       elif not guider.isSelected:
           return render(request,"guider_dashboard.html",{"msg":"Your approval is send to the Manager\nWait for approval"})
       else:
           return render(request,"guider_dashboard.html")
   elif request.method=="POST":
       form=specialityForm(request.POST or None,instance=guider)
       if form.is_valid():
           form.save()
           return redirect("guider_dashboard")


def communication_request(request):
    guider_id = request.session["id"]
    guider = Guider.objects.get(id=guider_id)
    guider_experties = guider.experties

    if request.method == "GET":
        consultation_user = investorConsultation.objects.filter(goal=guider_experties)
        user_data = [
            {
                "user": cu.user.id,
                "name": cu.user.name,
                "email": cu.user.email,
                "info": cu.info,
                "date": cu.prefered_date
            }
            for cu in consultation_user
        ]
        error=request.GET.get("error"," ")
        return render(request, "view_communication_request.html", {"data": user_data,"error":error})

    else:
        selected_users = request.POST.getlist("approve")

        if selected_users:
            # Perform bulk delete to avoid multiple queries
            investorConsultation.objects.filter(user__id__in=selected_users).delete()
            return redirect("guider_dashboard")
        else:
            return redirect(reverse("viewcommunication")+"?error=You have to select atleast one user")  # Ensure redirection happens if no selection

# def approve_consultation(request):

def organize_webinar(request):
    if request.method=="GET":
        form=WebinarRegisterForm()
        print("send form")
        error=request.GET.get("error","")
        return render(request,"webinar.html",{"form":form,"error":error})
    else:
        form=WebinarRegisterForm(request.POST)
        if form.is_valid():
            # print("something")
            instance=form.save(commit=False)
            print(f"Selected Date: {instance.date}, Today's Date: {date.today()}")

            if instance.date<date.today():
                redirect(reverse("organizewebinar")+"?error=Please enter valid date")
            instance.guider=Guider.objects.get(id=request.session["id"])
            instance.save()
        else:
            print("invalid")
            redirect(reverse("organizewebinar")+"?error=Please enter valid data input")
            
        return redirect("guider_dashboard")
    

def manage_user(request):
    if request.method=="GET":
        user_data = CustomUser.objects.filter(Q(role="investor") | Q(role="guider"))
        return render(request, 'manage_user.html',{"user_data":user_data})
    else:
        selected_users=request.POST.getlist('del')
        CustomUser.objects.filter(id__in=selected_users).delete()
        return render(request,"manager_dashboard.html")

def manage_subscriptions(request):
    if request.method == "GET":
        return render(request, 'manage_subscription.html')
    else:
        user_data = Investor.objects.filter(ispaid=True)

        for ud in user_data:
            if ud.payementDate and (date.today() - ud.payementDate).days >= 30:
                ud.ispaid = False
                ud.payementDate = None
                ud.save()

        all_users = Investor.objects.all()
        paid_users = Investor.objects.filter(ispaid=True)

        context = {
            "total": all_users.count(),
            "sub": paid_users.count(),
            "not_sub": all_users.count() - paid_users.count(),
            "user_data": paid_users
        }
        # print(context.get("total"))
        return render(request, "manage_subscription.html", {**context,"print":True})
        
def control_over_webinars(request):
    if request.method=="GET":
        webinar=Webinar.objects.filter(isApproved=False)
        webinar_data=[]
        for w in webinar:
            webinar_data.append({
                "id":w.id,
                "Topic":w.title,
                "Host":w.guider.name,
                "Date":w.date,
                "time":w.time
            })
        return render(request, 'control_over_web.html',{"webinar_data":webinar_data})  # Fix typo in URL name
    else:
        webinar_id=request.POST.get("webinar_id")
        action=request.POST.get("action")

        webinar=Webinar.objects.get(id=webinar_id)
        if action=="approve":
             webinar.isApproved=True
        elif action=="reject":
             webinar.isApproved=False
        webinar.save()
        return redirect("control_over_webinars")

def feedback(request):
    user_data=CustomUser.objects.filter(feedback!=None)
    feed=[]
    for user in user_data:
        feed.append({
            "id":user.id,
            "name":user.first_name+" "+user.last_name,
            "email":user.email,
            "fd":user.feedback
        })
    return render(request, 'feedback_manage.html',{"feedback":feed})


def guider_approve(request):
    if request.method=="GET":
        unapproved_guider=Guider.objects.filter(isSelected=False)
        return render(request,"manage_guider.html",{"guider_data":unapproved_guider})
    else:
        guider_id=request.POST.get("guider_id")
        action=request.POST.get("action")

        guider=Guider.objects.get(id=guider_id)
        if action=="approve":
            guider.isSelected=True
            guider.save()
        elif action=="reject":
            #first send email that you are not selected
            guider.delete()
        
        return redirect("guider_approve")