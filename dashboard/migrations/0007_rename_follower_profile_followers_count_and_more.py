# Generated by Django 5.0.6 on 2024-07-03 07:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_profile_follower_profile_following_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='follower',
            new_name='followers_count',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='following',
            new_name='following_count',
        ),
    ]
