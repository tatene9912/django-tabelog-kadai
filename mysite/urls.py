"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tabelog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tabelog.urls')),
    path('tabelog/', views.LocationView.as_view(), name="top"),
    path('tabelog/list', views.LocationListView.as_view(), name="location_list"),
    path('tabelog/detail/<int:pk>', views.LocationDetailView.as_view(), name="detail"),
    path('reserve/<int:location_id>/', views.ReservationCreateView.as_view(), name='reservation_create'),
    path('reservation/create/available_times/', views.ReservationCreateView.get_available_times, name='available_times'),
    path('account/', include('allauth.urls')), 
    path('add_favorite/<int:location_id>/', views.add_favorite, name='add_favorite'),
    path('mypage/', views.MyPage.as_view(), name="myPage"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('favorite/', views.FavoriteListView.as_view(), name="favorites_list"),
    path('favorites/remove/<int:pk>/', views.remove_favorite, name='remove_favorite'),
    path('config/', views.stripe_config),
    path('create_checkout_session/', views.create_checkout_session, name='checkout_session'),
    path('success/', views.success),
    path('cancel/', views.cancel),
    path('review/', views.ReviewListView.as_view(), name="review_list"),
    path('reviewUpdate/<int:pk>', views.ReviewUpdateView.as_view(), name='Review_update'),
    path('reviewDelete/<int:pk>', views.ReviewDeleteView.as_view(), name='Review_delete'),
    path('reservation/', views.ReservationListView.as_view(), name="reservation_list"),
    path('reservationDelete/<int:pk>', views.ReservationDeleteView.as_view(), name='reservation_delete'),
    path('checkout_success_webhook/', views.checkout_success_webhook, name='checkout_success_webhook'),
    path('cancelsubscription/', views.cancel_subscription, name='cancel_subscription'),
    path('cancel_subscription/', views.CancelSubscriptionView.as_view(), name='cancelSubscription'),
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('update_payment_method/', views.update_payment_method, name='update_payment_method'),
    path('update_payment_method_success/', views.PaymentUpdateSuccessView.as_view(), name='update_payment_method_success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
