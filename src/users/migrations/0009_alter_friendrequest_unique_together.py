# Generated by Django 5.0.1 on 2024-01-16 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_friendrequest_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friendrequest',
            unique_together={('from_user', 'to_user')},
        ),
    ]