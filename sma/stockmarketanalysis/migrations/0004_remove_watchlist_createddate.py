# Generated by Django 5.1.4 on 2025-02-22 05:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarketanalysis', '0003_investorconsultation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='createdDate',
        ),
    ]
