# Generated by Django 4.1.3 on 2022-11-20 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petition', '0004_signature_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='petition',
            name='recipient',
            field=models.EmailField(default='admin@admin.com', max_length=254),
        ),
    ]
