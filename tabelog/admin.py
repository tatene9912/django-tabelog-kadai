from django.contrib import admin

from tabelog.views import ImageFilter
from .models import Location, Category, Holiday, Reservation, Favorite, Review, Admin_user, Stripe_Customer
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget 

    
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
    list_display = ('id', 'customer', 'location', 'date', 'time','headcount', 'created_date', 'updated_date')
    search_fields = ('customer', 'location', )

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'location', 'created_date', 'updated_date')
    search_fields = ('customer', 'location', )

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'location', 'score', 'comment', 'created_date', 'updated_date')
    search_fields = ('customer', 'location', )
    list_display_links = ('location',)
    list_editable = ('score',)

class Admin_userAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'password', 'email', 'created_date', 'updated_date')
    search_fields = ('name', )

class Stripe_CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'stripeCustomerId', 'stripeSubscriptionId', 'stripePaymentMethodId', 'created_at', 'updated_at')
    search_fields = ('user', )

class LocationResource(ModelResource):
    name = Field(attribute='name', column_name='name')
    category = Field(attribute='category', column_name='category', widget=ManyToManyWidget(Category, 'id'))
    holiday = Field(attribute='holiday', column_name='holiday', widget=ManyToManyWidget(Holiday, 'id'))
    description = Field(attribute='description', column_name='description')
    capacity = Field(attribute='capacity', column_name='capacity')
    postal_code = Field(attribute='postal_code', column_name='postal_code')
    address = Field(attribute='address', column_name='address')
    phonenumber = Field(attribute='phonenumber', column_name='phonenumber')
    price_low = Field(attribute='price_low', column_name='price_low')
    price_high = Field(attribute='price_high', column_name='price_high')
    time_open = Field(attribute='time_open', column_name='time_open')
    time_close = Field(attribute='time_close', column_name='time_close')

    def image(self, obj):
        return mark_safe('<img src="{}" style="width:100px; height:auto;">'.format(obj.image.url))

    # def before_save_instance(self, instance, dry_run):
    #     # CSVからデータを取り込み、多対多フィールドを設定
    #     many_to_many_data = instance.category  # `category`がManyToManyFieldの例
    #     instance.save()  # インスタンスを一度保存してからセット
    #     instance.category.set(many_to_many_data)

    class Meta:
        model = Location
        skip_unchanged = True
        use_bulk = True
        exclude = ('some_abstract_field',) 

admin.site.register(Category, CategoryAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Admin_user, Admin_userAdmin)
admin.site.register(Stripe_Customer, Stripe_CustomerAdmin)

@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    ordering = ['id']
    list_display = ('id', 'name', 'thumbnail_image', 'description', 'capacity', 'postal_code', 'address', 'phonenumber', 'price_low', 'price_high', 'time_open', 'time_close', 'created_date', 'updated_date')
    search_fields = ('name', )
    resource_class = LocationResource
    ordering = ['id', 'price_low', 'price_high',]
    list_filter = ['capacity', 'price_low', 'price_high', ImageFilter] 

    def thumbnail_image(self, obj):
        return mark_safe('<img src="{}" style="width:100px; height:auto;">'.format(obj.image.url))

    thumbnail_image.short_description = 'Image'
