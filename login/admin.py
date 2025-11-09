from django.contrib import admin
from login.models import User

# Register your models here.

class SiteUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'is_active')

admin.site.register(User,SiteUserAdmin)
