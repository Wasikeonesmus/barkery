# Generated by Django 5.2.1 on 2025-06-05 01:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_purchase_amount_paid_purchase_checked_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='core.supplier'),
        ),
    ]
