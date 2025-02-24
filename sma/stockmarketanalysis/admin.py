from django.contrib import admin
from .models import *
class ManagerInline(admin.TabularInline):
    model=Guider
    extra =1

class customAdmin(admin.ModelAdmin):
    list_display=('username','email','role')
    list_filter=('role',)
    search_fields=('username','email','role')
    ordering=('username','role')
    inlines=[ManagerInline]

admin.site.register(CustomUser,customAdmin)
# Register your models here.
