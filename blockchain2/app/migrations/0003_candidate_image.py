# Generated by Django 4.1.5 on 2024-07-21 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_block_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='candidate_images/'),
        ),
    ]
