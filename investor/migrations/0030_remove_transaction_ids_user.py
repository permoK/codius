# Generated by Django 4.2.9 on 2024-02-26 19:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investor', '0029_alter_transaction_ids_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction_ids',
            name='user',
        ),
    ]