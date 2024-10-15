from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'birth_date', 'created_at', 'updated_at')
    search_fields = ('name', )

admin.site.register(User, UserAdmin) 
admin.site.unregister(Group)  