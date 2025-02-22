from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import get_object_or_404
from datetime import date
from .forms import *
# Create your views here.
def home(request):
    return render(request,'home.html',{'name':'Taksh','age':18})


# def paperTrading(request):
#     return render(request,'paperTrading.html')


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
                    else:
                        return render(request,"guider_dashboard.html")    
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

def guiderdashboard(request):
    return render(request,"guider_dashboard.html")


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