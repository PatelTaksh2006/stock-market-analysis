# Generated by Django 5.1.4 on 2025-03-08 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarketanalysis', '0006_remove_guider_availibility_customuser_feedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investorstock',
            name='no_of_purchase',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
