import datetime
from gettext import translation
import json
import logging
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.db.models import Avg, Q
from accounts.models import User
from .models import Favorite, Location,Reservation, Review
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FavoriteForm, ProfileForm, ReservationForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

class LocationView(ListView):
    model = Location
    template_name = "top.html"
    paginate_by = 10

class LocationListView(ListView):
    model = Location
    template_name = "location_list.html"
    paginate_by = 15
    context_object_name = 'locations'

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        query = self.request.GET

        if q := query.get('q'): 
            queryset = queryset.filter(Q(name__icontains=q)|Q(category__name__icontains=q))

        return queryset.order_by('-created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['search_count'] = self.get_queryset().count()
        context['query'] = query
        locations = self.get_queryset()
        location_ids = locations.values_list('id', flat=True)

        # 各店舗の平均レビュー点数を計算
        average_scores = Review.objects.filter(location_id__in=location_ids).values('location_id').annotate(average_score=Avg('score'))

        # 各店舗の平均点数と割合を辞書に格納
        average_score_dict = {}
        average_rate_dict = {}
        for score in average_scores:
            average = score['average_score']
            location_id = score['location_id']
            
            if average is not None:
                average_score_dict[location_id] = average
                average_rate = average / 5 * 100
                average_rate_dict[location_id] = average_rate
            else:
                average_score_dict[location_id] = 0
                average_rate_dict[location_id] = 0

        context['average_scores'] = average_score_dict
        context['average_rates'] = average_rate_dict

        # 各店舗ごとのレビュー件数を計算
        review_counts = {
            location.id: Review.objects.filter(location=location).count()
            for location in locations
        }
        context['review_counts'] = review_counts

        return context

class LocationDetailView(DetailView):
    model = Location
    template_name = "location_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = self.get_object() 
        user = self.request.user

        # お気に入りの状態をチェック
        if user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(customer=user, location=location).exists()
        else:
            context['is_favorite'] = False

        restid = self.kwargs['pk']
        review_count = Review.objects.filter(location_id=restid).count()
        score_ave = Review.objects.filter(location_id=restid).aggregate(Avg('score'))
        average = score_ave['score__avg']
        average_rate = average / 5 * 100
        context['review_count'] = review_count
        context['score_ave'] = score_ave
        context['average'] = average
        context['average_rate'] = average_rate
        review_list = Review.objects.filter(location_id=restid)
        context['review_list'] = review_list
        context['review_form'] = ReviewForm(user=user, location=location)


        # ユーザーが同じ店舗にレビューを投稿済みかどうかをチェック
        if self.request.user.is_authenticated:
            context['has_posted_review'] = Review.objects.filter(location=location, customer=self.request.user).exists()
        else:
            context['has_posted_review'] = False
        
        return context

    def post(self, request, *args, **kwargs):
        restid = self.kwargs['pk']
        review_form = ReviewForm(data=request.POST)
        try:
            location = Location.objects.get(id=restid)
        except Location.DoesNotExist:
            # location が存在しない場合のエラーハンドリング
            return redirect('some_error_page') 

        # ユーザーが同じ店舗にレビューを投稿済みかどうかをチェック
        if Review.objects.filter(location=location, customer=request.user).exists():
            context = self.get_context_data(**kwargs)
            context['error_message'] = ["この店舗にはすでにレビューを投稿しています。"]
            return self.render_to_response(context)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.location = location
            review.customer = request.user
            review.save()
            messages.success(self.request, 'レビューを投稿しました')
            return redirect('tabelog:location_detail', pk=location.pk)
        else:
            context = self.get_context_data(**kwargs)
            context['review_form'] = review_form
            context['error_message'] = review_form.non_field_errors() 
            return self.render_to_response(context)
        

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
    
