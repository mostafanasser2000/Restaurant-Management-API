# Generated by Django 5.0.6 on 2024-05-14 21:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_remove_menuitem_image"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cartitem",
            old_name="item",
            new_name="menuitem",
        ),
        migrations.AlterUniqueTogether(
            name="cartitem",
            unique_together={("cart", "menuitem")},
        ),
    ]
