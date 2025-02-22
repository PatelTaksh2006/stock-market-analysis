from django.urls import path

from . import views

urlpatterns=[
    path('',views.home,name="home"),
    path('login',views.login_page,name="login"),
    path('signup',views.signup,name="signup"),
    path('user_dashboard',views.userdashboard,name="user_dashboard"),
    path('guider_dashboard',views.guiderdashboard,name="guider_dashboard"),
    path('current_market_state', views.cms,name="current_market_state"),
    path('addToWatchlist/<name>',views.addToWatchlist,name="addToWatchlist"),
    path('papertrading',views.papertrading,name='papertrading'),
    path('webinar_registration',views.webinar_registration,name='webinar_registration'),
    path('marketanalysis',views.marketanalysis,name='marketanalysis'),
    path('sip',views.sip,name='sip'),
    path('consultation',views.consultation,name='consultation'),
    path('payment',views.payment,name="payment"),
    path('viewcommunication',views.communication_request,name="viewcommunication"),
    path('organizewebinar',views.organize_webinar,name="organizewebinar"),
    # path('approve_consultation',views.approve_consultation,name="approve_consultation"),  
]