# Generated by Django 5.0.6 on 2024-05-21 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_transaction_receipt_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
