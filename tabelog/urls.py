from django.urls import path
from . import views
from tabelog.views import LocationView, SubscriptionView, add_favorite, FavoriteListView, MyPage, edit_profile

app_name = 'tabelog'
urlpatterns = [
    # path('', views.TopView.as_view(), name="top"),
    path('', views.LocationView.as_view(), name="top"),
    path('reserve/<int:location_id>/', views.ReservationCreateView.as_view(), name='reservation_create'),
    path('detail/<int:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
    path('add_favorite/<int:location_id>/', views.add_favorite, name='add_favorite'),
    path('mypage/', MyPage.as_view(), name="myPage"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
]