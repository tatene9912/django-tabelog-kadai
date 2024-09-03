import datetime
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from .models import Location,Reservation
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ReservationForm

# class TopView(TemplateView):
#     template_name = "top.html"

class LocationView(ListView):
    model = Location
    template_name = "top.html"
    paginate_by = 10

class LocationDetailView(DetailView):
    model = Location
    template_name = "location_detail.html"

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