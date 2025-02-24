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
                        return render(request,"user_dashboard.html")
                    elif user.role=="guider":
                        guider=Guider.objects.get(user=user)
                        request.session["id"]=guider.id
                        return render(request,"guider_dashboard.html")
                    else:
                        return render(request,"manager_dashboard.html")    
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
        print("Login kar")
        form=LoginForm()
        return render(request,"login.html",{"form":form})
                            

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username=form.cleaned_data['username']
            # Prevent Investors from starting with a number
            # name=form.cleaned_data["name"]

            user.save()

            # Store Guider username for display (without "1" prefix)

            # Create corresponding entry in Investor or Guider
            if user.role == "investor":
                Investor.objects.create(name=user.username, email=user.email,user=user)
            elif user.role=="guider":
                Guider.objects.create(name=user.username, email=user.email,user=user)
            else:
                Manager.objects.create(name=user.username,email=user.email,user=user)
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

    if request.method=="GET":
        form=searchForm()
        return render(request,"current_market_state.html",{"form":form,"watchlist":watchlist_data})
    else:
        form=searchForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            print(name)
            # context={}
            # stock=Stock.objects.get(name=name)
            stock=get_object_or_404(Stock,name=name)
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



def papertrading(request):
    inv=Investor.objects.get(id=request.session["id"])
    user_stock=InvestorStock.objects.filter(investor=inv)
    stock_data=[]
    for investor_stock in user_stock:
        stock_data.append({
            'stock_name':investor_stock.stock.name,
            'stock_quantity':investor_stock.no_of_purchase,
            'price':investor_stock.price_of_buy,
            'current_price':investor_stock.stock.current_price
        })

        

    if request.method=="GET":
        form=PaperTradingStock()
        return render(request,"paper_trading.html",{"form":form,"data":stock_data})
    else:
        form=PaperTradingStock(request.POST)
        if form.is_valid():
            # instance=form.save(commit=False)
            buy_sell=form.cleaned_data["buy_sell"]
            stock_name=form.cleaned_data["stock_name"]
            quantity=form.cleaned_data["no_of_purchase"]
            stock=''
            investor=''
            stockOfInvestor=''
            try:
                stock=Stock.objects.get(name=stock_name)
                investor=Investor.objects.get(id=request.session['id'])
            except Stock.DoesNotExist:
                messages.error(request,"Stock doesn't exists")
                return redirect("papertrading")
            if buy_sell=="sell":
                try:
                    stockOfInvestor=InvestorStock.objects.get(stock=stock,investor=investor)
                except InvestorStock.DoesNotExist:
                    messages.error(request,"Stock doesn't exists in your buy list")
                    return redirect("papertrading")
                if quantity > stockOfInvestor.no_of_purchase:
                    messages.error(request,"Please Enter Valid amount")
                    return redirect("papertrading")
                stockOfInvestor.no_of_purchase-=quantity
                if stockOfInvestor.no_of_purchase==0:
                    stockOfInvestor.delete()
                else:
                    stockOfInvestor.save()
                return render(request,"user_dashboard.html")
            elif buy_sell=="buy":
                try:
                    stockOfInvestor=InvestorStock.objects.get(stock=stock,investor=investor)
                except InvestorStock.DoesNotExist:
                    instance=form.save(commit=False)
                    instance.investor=investor
                    instance.stock=stock
                    instance.no_of_purchase=quantity
                    instance.price_of_buy=stock.current_price
                    instance.save()
                    print("Successfully buy")
                    return render(request,"user_dashboard.html")
                
                stockOfInvestor.no_of_purchase+=quantity
                stockOfInvestor.save()
                # instance=stockOfInvestor
                return render(request,"user_dashboard.html")
            else:
                messages.error(request,"Please select appropriate option")
                return redirect("papertrading")
        else:
            messages.error("Please select appropriate option")
            return redirect("papertrading")
                
def webinar_registration(request):
    if request.method=="GET":
        form=WebinarForm()
        context={}
        context["web"]=Webinar.objects.all()
        if len(context["web"])>0:
            return render(request,"webinar_registration.html",{"register":True,"form":form})
        return render(request,"webinar_registration.html")
    else:
        form=WebinarForm(request.POST)
        if form.is_valid():
            selected=form.cleaned_data["web"]
            for webinar in selected:
                webinar.number_of_attendee+=1
                webinar.save()
        return render(request,"user_dashboard.html",{"message":"Successfully registered for given webinars"})
        

def marketanalysis(request):
    if request.method=="GET":
        form=searchForm()
        return render(request,"market_analy_pred.html",{"form":form})
    else:
        form=searchForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            try:
                stock=Stock.objects.get(name=name)
            except Stock.DoesNotExist:
                messages.error(request, "Given stock does not exist")
                return render(request, "market_analy_pred.html", {"form": form})
            # if stock is None:
            #     messages.error(request,"Given stock is not exist")
            #     return render(request,"market_analy_pred.html",{"form":form})
        return render(request,"market_analy_pred.html",{"form":form})
            

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
                messages.error(request,"Please correct the errors in the form.")
                return render(request,"consultation.html",{"form":ConsultationForm()})
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
            messages.error(request,"Please correct the errors in the form.")
            return render(request,"consultation.html",{"form":ConsultationForm()})
        
def payment(request):
    if request.method=="GET":
        form=payementForm()
        return render(request,"payement.html",{"form":form})
    else:
        form=payementForm(request.POST)
        if form.is_valid():
            expiry_date=form.cleaned_data["expiry_date"]
            today=date.today()
            if expiry_date<today:
                messages.error(request,"Please Enter valid card details")
                return render(request,"payement.html",{"form":form})
            investor=Investor.objects.get(id=request.session["id"])
            if investor.ispaid:
                messages.error(request,"Your subscription is active")
                return redirect("user_dashboard")
            else:
                investor.ispaid=True
                investor.save()
                messages.success(request,"You are upgraded to premium membership")
                return redirect("user_dashboard")
        else:
            messages.error(request,"Please enter valid input")
            print("error")
            return render(request,"payement.html",{"form":form})
        


def guiderdashboard(request):
    guider_id=request.session["id"]
    guider=Guider.objects.get(id=guider_id)
    if request.method=="GET":
        if not guider.experties:
            form=specialityForm()
            return render(request,"guider_dashboard.html",{"form":form})
        
        elif not guider.isSelected:
            return render(request,"guider_dashboard.html",{"msg":"Your approval is send to the Manager\nWait for approval"})
        else:
            return render(request,"guider_dashboard.html")
    else:
        form=specialityForm(request.POST or None,instance=guider)

        if form.is_valid():
            form.save()
            return redirect("guider_dashboard")




def communication_request(request):
    guider_id=request.session["id"]
    guider=Guider.objects.get(id=guider_id)
    guider_experties=guider.experties
    if request.method=="GET":
        consultation_user=investorConsultation.objects.filter(goal=guider_experties)
        user_data=[]
        for cu in consultation_user:
            user_data.append({
                "user":cu.user.id,
                "name":cu.user.name,
                "email":cu.user.email,
                "info":cu.info,
                "date":cu.prefered_date
            })
        return render(request,"view_communication_request.html",{"data":user_data})
    else:
        selected_user=request.POST.getlist("approve")
        for su in selected_user:
            investor=investorConsultation.objects.get(user=su)
            investor.delete()
        
        return redirect("guider_dashboard")
# def approve_consultation(request):

def organize_webinar(request):
    if request.method=="GET":
        form=WebinarRegisterForm()
        print("send form")
        return render(request,"webinar.html",{"form":form})
    else:
        form=WebinarRegisterForm(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.guider=Guider.objects.get(id=request.session["id"])
            instance.save()
        
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