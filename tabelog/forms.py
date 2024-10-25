from django import forms
from accounts.models import User
from django.core.exceptions import ValidationError
from .models import Favorite, Location, Reservation, Review

class ReservationForm(forms.ModelForm):
    HEADCOUNT_CHOICES = [(i, f'{i}名') for i in range(1, 11)]
    
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='予約日')
    headcount = forms.ChoiceField(choices=HEADCOUNT_CHOICES, label="予約人数")

    class Meta:
        model = Reservation
        fields = ['date', 'headcount']

    def __init__(self, *args, **kwargs):
        location_id = kwargs.pop('location_id', None)
        super().__init__(*args, **kwargs)

        if location_id:
            self.location = Location.objects.get(pk=location_id)




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