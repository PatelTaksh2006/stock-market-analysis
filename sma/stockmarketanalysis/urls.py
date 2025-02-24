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
    path('manage_user/', views.manage_user, name='manage_user'),
    path('manage_subscriptions/', views.manage_subscriptions, name='manage_subscriptions'),
    path('contorl_over_web/', views.control_over_webinars, name='control_over_webinars'),
    # path('feedback/', views.feedback, name='feedback'),
    # path('approve_consultation',views.approve_consultation,name="approve_consultation"),  
    path('guider_manage', views.guider_approve, name='guider_approve'),
    path('feedback_page',views.feedback_page,name="feedback"),
    path('logout',views.logout_request,name="logout_request"),
]