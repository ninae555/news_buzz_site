# Generated by Django 4.2.5 on 2024-02-11 15:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_alter_session_end_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="participant",
            name="first_name",
            field=models.CharField(
                blank=True, default=None, max_length=255, null=True, verbose_name="First Name of Participant"
            ),
        ),
        migrations.AddField(
            model_name="participant",
            name="login_website_type",
            field=models.CharField(
                blank=True, default=None, max_length=255, null=True, verbose_name="Website accesed High / Low PC1"
            ),
        ),
    ]
