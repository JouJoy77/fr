# Generated by Django 4.2.3 on 2023-07-10 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_mailing_time_interval'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='filter_code',
            field=models.CharField(blank=True, max_length=3, null=True, verbose_name='Фильтр кода оператора'),
        ),
        migrations.AddField(
            model_name='mailing',
            name='filter_tag',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Фильтр тега'),
        ),
    ]