# Generated by Django 5.2.1 on 2025-05-26 12:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0002_remove_book_id_remove_loan_book_remove_loan_id_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="loan",
            name="is_overdue",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="loan",
            name="userID",
            field=models.ForeignKey(
                db_column="userID",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="loans",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
