# Generated by Django 5.1 on 2024-10-04 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_alter_product_colors_alter_product_sizes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='color',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='size',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
