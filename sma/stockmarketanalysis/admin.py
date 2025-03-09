from django.contrib import admin
from .models import *

# Register CustomUser with extra admin options
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

# Register other models with default ModelAdmin
@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'mobile_no', 'investedAmount', 'ispaid')
    search_fields = ('name', 'email')

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'mobile_no')
    search_fields = ('name', 'email')

@admin.register(Guider)
class GuiderAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'experties', 'isSelected')
    search_fields = ('name', 'email')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_price', 'volume', 'sector')
    search_fields = ('name', 'sector')

@admin.register(InvestorStock)
class InvestorStockAdmin(admin.ModelAdmin):
    list_display = ('investor', 'stock', 'no_of_purchase', 'price_of_buy')
    search_fields = ('investor__name', 'stock__name')

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('investor', 'stock')
    search_fields = ('investor__name', 'stock__name')

@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = ('guider', 'title', 'date', 'time', 'duration', 'isApproved')
    search_fields = ('title', 'guider__name')

@admin.register(investorConsultation)
class InvestorConsultationAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'prefered_date', 'info')
    search_fields = ('user__name', 'goal')


@admin.register(UserWebinar)
class UserWebinarAdmin(admin.ModelAdmin):
    list_display=('investor','webinar')
    search_fields=('investor','webinar')

