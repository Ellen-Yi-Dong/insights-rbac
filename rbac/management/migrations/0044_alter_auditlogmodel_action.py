# Generated by Django 4.1.7 on 2023-08-23 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0043_remove_auditlogmodel_tenant"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditlogmodel",
            name="action",
            field=models.CharField(
                choices=[
                    ("add", "Add"),
                    ("delete", "Delete"),
                    ("create", "Create"),
                    ("edit", "Edit"),
                ],
                max_length=32,
            ),
        ),
    ]