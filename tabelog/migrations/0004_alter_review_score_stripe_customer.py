# Generated by Django 5.1 on 2024-09-22 07:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tabelog', '0003_alter_review_score_alter_review_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.PositiveSmallIntegerField(choices=[(1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')], default=3, verbose_name='評価'),
        ),
        migrations.CreateModel(
            name='Stripe_Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripeCustomerId', models.CharField(max_length=255)),
                ('stripeSubscriptionId', models.CharField(max_length=255)),
                ('regist_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
