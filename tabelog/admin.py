from django.contrib import admin
from .models import Locations, Categories, Holidays
from django.utils.safestring import mark_safe

class LocationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'holiday', 'image', 'description', 'capacity', 'postal_code', 'address', 'phonenumber', 'price_low', 'price_high', 'time_open', 'time_close', 'created_date', 'updated_date')

    def image(self, obj):
        return mark_safe('<img src="{}" style="width:100px height:auto;">'.format(obj.img.url))
    
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )

class HolidaysAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )

admin.site.register(Categories)
admin.site.register(Holidays)
admin.site.register(Locations, LocationsAdmin)