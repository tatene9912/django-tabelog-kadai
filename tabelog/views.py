from datetime import datetime, timedelta
from gettext import translation
from django.utils import timezone
import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Avg, Q
import stripe
from accounts.models import User
from django.contrib import admin
from .models import Favorite, Location,Reservation, Review, Stripe_Customer
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FavoriteForm, ProfileForm, ReservationForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.utils.timezone import now

class ImageFilter(admin.SimpleListFilter):
    title = '画像が未登録'
    parameter_name = 'image_filter'

    def lookups(self, request, model_admin):
        return (
            ('yes', '画像が未登録'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(image='noImage.png')  # デフォルトの画像を確認
        return queryset

class LocationView(ListView):
    model = Location
    template_name = "top.html"

    def get_queryset(self):
        # 新着店舗を作成日の降順で取得し、先頭から10件を取得
        return Location.objects.order_by('-created_date')[:10]

class LocationListView(ListView):
    model = Location
    template_name = "location_list.html"
    paginate_by = 15
    context_object_name = 'locations'

    SORT_OPTIONS = [
        {'key': 'price_high', 'value': '価格が高い順'},
        {'key': 'price_low', 'value': '価格が低い順'},
        {'key': 'rating_high', 'value': '評価が高い順'},
        {'key': 'rating_low', 'value': '評価が低い順'},
        {'key': 'created_date', 'value': '新しい順'},
        {'key': 'name', 'value': '名前順'},
    ]

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        query = self.request.GET

        if q := query.get('q'): 
            queryset = queryset.filter(Q(name__icontains=q)|Q(category__name__icontains=q))

        # 並び替えの処理
        sort = query.get('order_by')
        if sort == 'price_high':
            queryset = queryset.order_by('-price_high')
        elif sort == 'price_low':
            queryset = queryset.order_by('price_low')
        elif sort == 'rating_high':
            queryset = queryset.annotate(average_score=Avg('review__score')).order_by('-average_score')
        elif sort == 'rating_low':
            queryset = queryset.annotate(average_score=Avg('review__score')).order_by('average_score')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            # デフォルトは作成日順
            queryset = queryset.order_by('-created_date')

        return queryset

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

        # 並び替えオプションをコンテキストに追加
        context['sort_list'] = self.SORT_OPTIONS

        # 現在の並び替えオプションをコンテキストに追加
        context['current_sort'] = self.request.GET.get('order_by', 'created_date')

        return context

class SubscriptionView(TemplateView):
    template_name = 'subscription.html'

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

        # averageがNoneの場合、average_rateの計算をスキップまたはデフォルト値を設定
        if average is not None:
            average_rate = average / 5 * 100
        else:
            average_rate = 0  # デフォルト値として0を設定

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
        
class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'review_list.html'
    paginate_by = 10

    def get_queryset(self):
        # ログイン中のユーザーに関連するレビューのみをフィルタリング
        return Review.objects.filter(customer=self.request.user).select_related('location')

class ReviewUpdateView(UpdateView):
    model = Review
    fields = ['score', 'comment']
    template_name = 'review_update.html'

    def form_valid(self, form):
        review = form.save(commit=False)
        print(f"Score: {review.score}, Comment: {review.comment}")
        review.updated_date = now()
        review.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.info(self.request, 'レビューを編集しました。')
        return reverse_lazy('review_list')
    
class ReviewDeleteView(DeleteView):
    model = Review
    template_name = 'review_delete.html'

    def get_success_url(self):
        messages.info(self.request, 'レビューを削除しました。')
        return reverse_lazy('review_list')

class ReservationCreateView(CreateView):
    form_class = ReservationForm
    template_name = 'reservation_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = get_object_or_404(Location, pk=self.kwargs['location_id'])
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['location_id'] = self.kwargs['location_id']
        return kwargs
    
    def form_invalid(self, form):
        print("Form is invalid. Errors: ", form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        location = get_object_or_404(Location, pk=self.kwargs['location_id'])
        reservation = form.save(commit=False)
        reservation.location = location
        reservation.customer = self.request.user
        reservation.time = self.request.POST['time']


        # 選択された予約日が過去日であれば予約を無効にする
        if reservation.date < timezone.now().date():
            messages.error(self.request, '本日以降の日付を選択してください。')
            return self.form_invalid(form)

        if Reservation.objects.filter(location=location, date=reservation.date, time=reservation.time).exists():
            messages.error(self.request, '予約がいっぱいです。別の時間でご予約ください。')
            return self.form_invalid(form)

        reservation.save()
        messages.success(self.request, '予約が完了しました。')
        return redirect('reservation_list')

    @staticmethod
    def get_available_times(request):
        date_str = request.GET.get('date')
        location_id = request.GET.get('location_id')

        if date_str and location_id:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return HttpResponseBadRequest("Invalid date format")

            location = get_object_or_404(Location, pk=location_id)
            now = datetime.now()
            open_time = location.time_open
            close_time = location.time_close
            available_times = []

            # 時刻を次の30分単位に切り上げる関数
            def round_up_time(dt):
                if dt.minute == 0 or dt.minute == 30:
                    return dt
                return (dt + timedelta(minutes=30 - dt.minute % 30)).replace(second=0, microsecond=0)


            # 当日の場合
            if date == now.date():
                current_time = now.replace(second=0, microsecond=0)
                rounded_time = round_up_time(current_time)
                two_hours_later = rounded_time + timedelta(hours=2)
                if two_hours_later.time() > open_time:
                    open_time = two_hours_later.time()

            # 営業時間内の30分間隔の時間候補を生成
            current_datetime = datetime.combine(date, open_time)
            close_datetime = datetime.combine(date, close_time)

            # close_time が open_time よりも早い場合、閉店時間を翌日に設定
            if close_time < open_time:
                close_datetime += timedelta(days=1)

            while current_datetime < close_datetime:
                time_str = current_datetime.strftime('%H:%M')
                available_times.append(time_str)
                current_datetime += timedelta(minutes=30)


            return JsonResponse(available_times, safe=False)

        return JsonResponse([], safe=False)




    
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
            messages.info(request, 'お気に入りに追加しました。')
            return redirect('favorites_list')
    else:
        form = FavoriteForm()
    
    return render(request, 'location_detail.html', {'form': form})

class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'favorites_list.html'
    paginate_by = 10

    def get_queryset(self):
        # ログイン中のユーザーに関連するお気に入りのみをフィルタリング
        return Favorite.objects.filter(customer=self.request.user).select_related('location')
    
@login_required
def remove_favorite(request, pk):
    favorite = get_object_or_404(Favorite, pk=pk, customer=request.user)
    favorite.delete()
    messages.success(request, 'お気に入りを解除しました。')
    return redirect('favorites_list')

class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservation_list.html'
    paginate_by = 5
    context_object_name = 'reservations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 予約の詳細を取得する際にpkを正しく設定
        context['detail_url'] = {reservation.id: reverse('detail', kwargs={'pk': reservation.id}) for reservation in self.object_list}
        return context
    
    def get_queryset(self):
        # ログイン中のユーザーに関連する予約のみをフィルタリング
        return Reservation.objects.filter(customer=self.request.user).select_related('location')
    
class ReservationDeleteView(DeleteView):
    model = Reservation
    template_name = 'reservation_delete.html'

    def get_success_url(self):
        messages.info(self.request, '予約を削除しました。')
        return reverse_lazy('reservation_list')

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
        return context
    
@method_decorator(login_required,name="dispatch")
class SubscriptionView(TemplateView):
    template_name = 'subscription.html'
    model = User
    
# 設定用の処理
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)

# 支払い画面に遷移させるための処理
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'https://mynagoyameshi-6001a0ebbfca.herokuapp.com/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # ユーザーが認証されているか確認
        if request.user.is_authenticated:
            # ユーザーがすでに Stripe カスタマーであるか確認
            if hasattr(request.user, 'stripe_customer'):

                return redirect('cancel_subscription')  
            
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id,
                    success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url + 'cancel/',
                    payment_method_types=['card'],
                    mode='subscription',
                    line_items=[
                        {
                            'price': settings.STRIPE_PRICE_ID,
                            'quantity': 1,
                        }
                    ]
                )
                return redirect(checkout_session.url)
            except Exception as e:
                return JsonResponse({'error': str(e)})

endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

@csrf_exempt
def checkout_success_webhook(request):
    payload = request.body
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # 顧客情報を確認
        customer_id = session['customer']

        # 顧客情報をStripeから取得
        customer = stripe.Customer.retrieve(customer_id)
        email = customer['email']

        # 支払い方法を取得するためのAPI呼び出し
        payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type="card"
        )
        
        if payment_methods.data:
            payment_method_id = payment_methods.data[0].id  # 最初の支払い方法を取得
        else:
            payment_method_id = None

        try:
            user = User.objects.get(email=email)

            # Stripe_Customerの取得または作成
            stripe_customer, created = Stripe_Customer.objects.get_or_create(
                user=user,
                defaults={
                    'stripeCustomerId': customer_id,  # 顧客ID
                    'stripeSubscriptionId': session.get('subscription', None),  # サブスクリプションID
                    'stripePaymentMethodId': payment_method_id  # 支払い方法ID
                }
            )
            if not created:
                stripe_customer.stripeSubscriptionId = session.get('subscription', None)
                stripe_customer.stripePaymentMethodId = payment_method_id  # 支払い方法IDを更新
                stripe_customer.save()

        except User.DoesNotExist:
            print(f"User with email {email} does not exist.")
        except Exception as e:
            print(f"Error in fulfilling order: {str(e)}")

    elif event['type'] == 'invoice.payment_succeeded':
        pass

    return HttpResponse(status=200)



# 支払いに成功した後の画面
def success(request):
    return render(request, 'success.html')

# 支払いに失敗した後の画面
def cancel(request):
    return render(request, 'cancel.html')

@csrf_exempt
@login_required
def update_payment_method(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')
            subscription_id = data.get('subscription_id')

            if not payment_method_id:
                return JsonResponse({'status': 'error', 'message': 'Payment method ID is missing'})

            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # サブスクリプションから古い支払い方法を取得
            subscription = stripe.Subscription.retrieve(subscription_id)
            old_payment_method_id = subscription.default_payment_method

            if old_payment_method_id:
                # 古い支払い方法のデタッチ
                stripe.PaymentMethod.detach(old_payment_method_id)

            # 新しいカード情報を顧客にアタッチ
            customer = subscription.customer
            stripe.PaymentMethod.attach(payment_method_id, customer=customer)

            # デフォルトの支払い方法を更新
            stripe.Customer.modify(
                customer,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                },
            )

            # Stripe_Customerを取得し、支払い方法IDを更新
            stripe_customer = Stripe_Customer.objects.get(user=request.user)
            stripe_customer.stripePaymentMethodId = payment_method_id  # 新しい支払い方法IDを保存
            stripe_customer.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'GET':
        try:
            # 現在のユーザーに関連するStripe_Customerを取得
            subscription = Stripe_Customer.objects.get(user=request.user)
            subscription_id = subscription.stripeSubscriptionId  # サブスクリプション ID
            old_payment_method_id = subscription.stripePaymentMethodId  # 古い支払い方法 ID
        except Stripe_Customer.DoesNotExist:
            subscription_id = None
            old_payment_method_id = None  # 古い支払い方法 ID がない場合の処理
        
        context = {
            'subscription_id': subscription_id,
            'old_payment_method_id': old_payment_method_id,  # 古い支払い方法 ID をコンテキストに追加
        }
        return render(request, 'update_payment_method.html', context)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})



class PaymentUpdateSuccessView(TemplateView):
    template_name = 'update_payment_method_success.html'

class CancelSubscriptionView(TemplateView):
    template_name = 'cancel_subscription.html'


def cancel_subscription(request):
    if request.user.is_authenticated:
        try:
            # StripeのAPIキーを設定
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            stripe_customer = request.user.stripe_customer  # Stripe カスタマー情報を取得
            subscription_id = stripe_customer.stripeSubscriptionId  # サブスクリプションIDを取得

            # Stripe APIを使ってサブスクリプションをキャンセル
            stripe.Subscription.delete(subscription_id)

            # Stripe_Customerレコードを削除
            stripe_customer.delete()

            return render(request, 'cancel_success.html')  # 解約成功ページにリダイレクト

        except stripe.error.StripeError as e:
            # Stripe APIでのエラー処理
            return redirect('error_page')  # エラーページにリダイレクト

        except Exception as e:
            # その他のエラー処理
            return redirect('error_page')  # エラーページにリダイレクト
    else:
        return redirect('login')  # 認証されていない場合はログインページへ