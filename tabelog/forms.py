from django import forms
from .models import Favorite, Location, Reservation

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