# Generated by Django 4.0.2 on 2022-05-23 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('choice_model', '0003_baselinesite_baseline_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baselinesite',
            name='baseline_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='choice_model.baselinemodel'),
        ),
    ]
