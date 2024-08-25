from django.contrib import admin
from .models import Location, Category, Holiday, Customer, Reservation, Favorite, Review, Admin_user
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_date', 'updated_date')
    search_fields = ('name', )

class HolidayAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_date', 'updated_date')
    search_fields = ('name', )

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'furigana', 'email', 'password', 'membership_flg', 'created_date', 'updated_date')
    search_fields = ('name', )

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'location', 'datetime', 'headcount', 'created_date', 'updated_date')
    search_fields = ('customer', 'location', )

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'location', 'created_date', 'updated_date')
    search_fields = ('customer', 'location', )

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'location', 'score', 'comment', 'created_date', 'updated_date')
    search_fields = ('customer', 'location', )

class Admin_userAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'password', 'email', 'created_date', 'updated_date')
    search_fields = ('name', )

class LocationResource(ModelResource):
    name = Field(attribute='name', column_name='name')
    category = Field(attribute='category', column_name='category', widget=ForeignKeyWidget(Category, 'name'))
    holiday = Field(attribute='holiday', column_name='holiday', widget=ForeignKeyWidget(Holiday, 'name'))
    description = Field(attribute='description', column_name='description')
    capacity = Field(attribute='capacity', column_name='capacity')
    postal_code = Field(attribute='postal_code', column_name='postal_code')
    address = Field(attribute='address', column_name='address')
    phonenumber = Field(attribute='phonenumber', column_name='phonenumber')
    price_low = Field(attribute='price_low', column_name='price_low')
    price_high = Field(attribute='price_high', column_name='price_high')
    time_open = Field(attribute='time_open', column_name='time_open')
    time_close = Field(attribute='time_close', column_name='time_close')

    class Meta:
        model = Location
        skip_unchanged = True
        use_bulk = True

admin.site.register(Category, CategoryAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Admin_user, Admin_userAdmin)

@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    ordering = ['id']
    list_display = ('id', 'name', 'image', 'description', 'capacity', 'postal_code', 'address', 'phonenumber', 'price_low', 'price_high', 'time_open', 'time_close', 'created_date', 'updated_date')
    search_fields = ('name', )
    resource_class = LocationResource

    def image(self, obj):
        return mark_safe('<img src="{}" style="width:100px height:auto;">'.format(obj.img.url))