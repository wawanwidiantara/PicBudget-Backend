# Generated by Django 5.1.2 on 2024-11-13 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo_url',
            field=models.ImageField(blank=True, null=True, upload_to='profile/'),
        ),
    ]