from django.contrib import admin
from .models import Locations, Categories
from django.utils.safestring import mark_safe

class LocationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'image')

    def image(self, obj):
        return mark_safe('<img src="{}" style="width:100px height:auto;">'.format(obj.img.url))
    
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )

admin.site.register(Categories)
admin.site.register(Locations, LocationsAdmin)