# Generated by Django 5.0.1 on 2024-02-13 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_chatroom_is_direct_message_alter_chatroom_members'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(max_length=150),
        ),
    ]
