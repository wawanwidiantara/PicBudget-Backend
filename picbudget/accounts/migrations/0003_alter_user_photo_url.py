# Generated by Django 5.1.2 on 2024-11-13 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_photo_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo_url',
            field=models.ImageField(blank=True, default='profile/default.jpg', null=True, upload_to='profile/'),
        ),
    ]