# Generated by Django 4.2.9 on 2024-07-07 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investor', '0078_mpesatransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='profit_released_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        
    ]
