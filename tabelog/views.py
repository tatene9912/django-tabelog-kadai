import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView

from accounts.models import User
from .models import Favorite, Location,Reservation
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FavoriteForm, ProfileForm, ReservationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

# class TopView(TemplateView):
#     template_name = "top.html"

class LocationView(ListView):
    model = Location
    template_name = "top.html"
    paginate_by = 10

class LocationDetailView(DetailView):
    model = Location
    template_name = "location_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = self.object
        user = self.request.user

        # お気に入りの状態をチェック
        if user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(customer=user, location=location).exists()
        else:
            context['is_favorite'] = False

        return context

class ReservationCreateView(CreateView):
    form_class = ReservationForm
    template_name = 'reservation_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = get_object_or_404(Location, pk=self.kwargs['location_id'])
        return context

    def form_valid(self, form):
        location = get_object_or_404(Location, pk=self.kwargs['location_id'])
        reservation = form.save(commit=False)
        reservation.location = location
        reservation.customer = self.request.user  # 現在ログインしているユーザーを設定
        
        # 日時の組み立て
        try:
            reservation_datetime = datetime.datetime.combine(reservation.date, reservation.time)
        except ValueError:
            messages.error(self.request, '不正な日時が指定されました。')
            return self.form_invalid(form)
        
        if Reservation.objects.filter(location=location, date=reservation.date, time=reservation.time).exists():
            messages.error(self.request, 'すみません、入れ違いで予約がありました。別の日時はどうですか。')
            return self.form_invalid(form)
        
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'ログインが必要です。')
            return self.form_invalid(form)
        
        reservation.save()
        messages.success(self.request, '予約が完了しました。')
        return redirect('tabelog:location_detail', pk=location.pk)
    
def add_favorite(request, location_id):
    if request.method == 'POST':
        # 既存のお気に入りをチェック
        if Favorite.objects.filter(customer=request.user, location_id=location_id).exists():
            messages.info(request, 'すでにお気に入りに追加されています。')
            return redirect('tabelog:location_detail', pk=location_id)

        form = FavoriteForm(request.POST)
        if form.is_valid():
            favorite = form.save(commit=False)
            favorite.customer = request.user  # ログイン中のユーザーを設定
            favorite.location_id = location_id
            favorite.save()
            messages.success(request, 'お気に入りに追加しました。')
            return redirect('tabelog:location_detail', pk=location_id)
    else:
        form = FavoriteForm()
    
    return render(request, 'location_detail.html', {'form': form})

class FavoriteListView(ListView):
    model = Favorite
    template_name = 'favorite-list.html'

@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('myPage')
    else:
        profile_form = ProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {
        'profile_form': profile_form,
    })

class MyPage(LoginRequiredMixin, TemplateView):
    template_name = 'myPage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user 
        # context['favorites'] = Favorite.objects.filter(customer=User)
        # context['reservations'] = Reservation.objects.filter(customer=User)
        return context