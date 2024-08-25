from allauth.account.forms import SignupForm
from .models import User

class CustomSignupForm(SignupForm):
    class Meta:
        model = User
        fields = ['email', 'account_id', 'password1', 'password2']


