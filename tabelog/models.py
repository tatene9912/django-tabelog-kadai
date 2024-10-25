from django.conf import settings
from django.db import models

from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=20, verbose_name='カテゴリ名')
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    
class Holiday(models.Model):
    name = models.CharField(max_length=50, verbose_name='休日名')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=50, verbose_name='店舗名')
    category = models.ManyToManyField(Category, verbose_name='カテゴリ', blank=True)
    holiday = models.ManyToManyField(Holiday, verbose_name='店休日', blank=True)
    image = models.ImageField(blank=True, default='noImage.png', verbose_name='画像')
    description = models.TextField(max_length=200, verbose_name='説明', null=True)
    capacity = models.IntegerField(verbose_name='定員', null=True)
    postal_code = models.CharField(max_length=7, verbose_name='郵便番号', null=True)
    address = models.CharField(max_length=50, verbose_name='住所', null=True)
    phonenumber = models.CharField(max_length=11, verbose_name='電話番号', null=True)
    price_low = models.IntegerField(verbose_name='下限金額', null=True)
    price_high = models.IntegerField(verbose_name='上限金額', null=True)
    time_open = models.TimeField(verbose_name='開店時間', null=True)
    time_close = models.TimeField(verbose_name='閉店時間', null=True)
    created_date = models.DateTimeField(verbose_name='作成日時', auto_now_add=True, null=True)
    updated_date = models.DateTimeField(verbose_name='更新日時', auto_now=True, null=True)

    def __str__(self):
        return self.name
    
class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='予約者名')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='店舗名')
    date = models.DateField(verbose_name='予約日', null=True)
    time = models.TimeField(verbose_name='予約時間', null=True)
    headcount = models.IntegerField(verbose_name='予約人数')
    created_date = models.DateTimeField(verbose_name='作成日時', auto_now_add=True, null=True)
    updated_date = models.DateTimeField(verbose_name='更新日時', auto_now=True, null=True)

    def __str__(self):
        return f"Reservation by {self.customer.name} at {self.location.name} on {self.date}"


    
class Favorite(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー名')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='店舗名')
    created_date = models.DateTimeField(verbose_name='作成日時', auto_now_add=True, null=True)
    updated_date = models.DateTimeField(verbose_name='更新日時', auto_now=True, null=True)

    def __str__(self):
        return f"Favorite by {self.customer.email} at {self.location.name}"
    
SCORE_CHOICES = [
    (1, '★'),
    (2, '★★'),
    (3, '★★★'),
    (4, '★★★★'),
    (5, '★★★★★'),
]
    
class Review(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー名')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='店舗名')
    score = models.PositiveSmallIntegerField(verbose_name='評価', choices=SCORE_CHOICES, default=3)
    comment = models.TextField(null=True, verbose_name='コメント')
    created_date = models.DateTimeField(verbose_name='作成日時', auto_now_add=True, null=True)
    updated_date = models.DateTimeField(verbose_name='更新日時', auto_now=True, null=True)

    class Meta:
        unique_together = ('location', 'customer')

    def __str__(self):
        return f"Favorite by {self.customer.email} at {self.location.name}"
    
    def get_percent(self):
        percent = round(self.score / 5 * 100)
        return percent
    
class Stripe_Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stripe_customer')
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255, null=True, blank=True)
    stripePaymentMethodId = models.CharField(max_length=255, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stripe Customer for {self.user.email}"
    
class Admin_user(models.Model):
    name = models.CharField(max_length=50, verbose_name='氏名')
    password = models.CharField(max_length=50, verbose_name='パスワード')
    email = models.EmailField(verbose_name='メールアドレス')
    created_date = models.DateTimeField(verbose_name='作成日時', auto_now_add=True, null=True)
    updated_date = models.DateTimeField(verbose_name='更新日時', auto_now=True, null=True)

    def __str__(self):
        return self.name