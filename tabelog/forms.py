import datetime
from django import forms
from accounts.models import User
from django.core.exceptions import ValidationError
from .models import Favorite, Location, Reservation, Review

class ReservationForm(forms.ModelForm):
    HEADCOUNT_CHOICES = [(i, f'{i}名') for i in range(1, 11)]
    
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='予約日')
    time = forms.ChoiceField(choices=[], label="予約時間")
    headcount = forms.ChoiceField(choices=HEADCOUNT_CHOICES, label="予約人数")

    class Meta:
        model = Reservation
        fields = ['date', 'time', 'headcount']

    def __init__(self, *args, **kwargs):
        location_id = kwargs.pop('location_id', None)
        super().__init__(*args, **kwargs)

        if location_id:
            self.location = Location.objects.get(pk=location_id)
            self.fields['time'].choices = self.get_available_times()

    def get_available_times(self, date=None):
        available_times = []
        if not self.location or not self.location.time_open or not self.location.time_close:
            return available_times

        opening_time = self.location.time_open
        closing_time = self.location.time_close

        # 日付が指定されている場合は、その日付に基づくロジックを実行
        if date:
            current_time = datetime.datetime.now()
            two_hours_later = current_time + datetime.timedelta(hours=2)
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            opening_datetime = datetime.datetime.combine(date_obj, opening_time)
            closing_datetime = datetime.datetime.combine(date_obj, closing_time)

            # 営業時間内の時間を生成
            time = opening_datetime
            while time <= closing_datetime:
                if time >= two_hours_later:
                    available_times.append((time.strftime("%H:%M"), time.strftime("%H:%M")))
                time += datetime.timedelta(minutes=30)
        return available_times


class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = [] 

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'birth_date', 'email',)
        widgets = {
            'birth_date': forms.DateInput(attrs={'type':'date'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['score', 'comment']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.location = kwargs.pop('location', None)
        super().__init__(*args, **kwargs)

        # フォームがバインドされている場合（POSTリクエスト時）にのみ、重複チェックを行う
        if self.user and self.location and self.data:
            if Review.objects.filter(customer=self.user, location=self.location).exists():
                self.add_error(None, ValidationError("同じ店舗に複数のレビューを投稿することはできません。"))