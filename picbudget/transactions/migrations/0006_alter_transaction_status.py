# Generated by Django 5.1.2 on 2024-11-14 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_alter_transaction_wallet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('confirmed', 'Confirmed'), ('unconfirmed', 'Unconfirmed')], default='confirmed', max_length=12),
        ),
    ]