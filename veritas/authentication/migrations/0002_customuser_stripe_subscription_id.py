# Generated by Django 4.0.2 on 2022-08-18 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='stripe_subscription_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]