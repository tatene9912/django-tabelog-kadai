from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'birth_date', 'created_date', 'updated_date')
    search_fields = ('name', )

    admin.site.register(User)  # Userモデルを登録
admin.site.unregister(Group)  # Groupモデルは不要のため非表示