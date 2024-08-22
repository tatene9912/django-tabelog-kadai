from django.db import models

class Categories(models.Model):
    name = models.CharField(max_length=20, verbose_name='カテゴリ名')
    created_date = models.TimeField(auto_now_add=True, null=True)
    updated_date = models.TimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    
class Holidays(models.Model):
    name = models.CharField(max_length=50, verbose_name='休日名')
    created_date = models.TimeField(auto_now_add=True)
    updated_date = models.TimeField(auto_now=True)

    def __str__(self):
        return self.name

class Locations(models.Model):
    name = models.CharField(max_length=50, verbose_name='店名')
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, verbose_name='カテゴリ')
    holiday = models.ForeignKey(Holidays, on_delete=models.CASCADE, verbose_name='店休日', null=True)
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