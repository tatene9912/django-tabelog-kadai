from django import forms
from accounts.models import User
from django.core.exceptions import ValidationError
from .models import Favorite, Location, Reservation, Review

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'time', 'headcount']
        widgets = {
            'date': forms.DateInput(attrs={'type':'date'}),
            'time': forms.TimeInput(attrs={'type':'time'}),
        }

class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = [] 

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'birth_date')
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