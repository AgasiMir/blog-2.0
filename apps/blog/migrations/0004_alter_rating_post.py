# Generated by Django 4.2.11 on 2024-04-28 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_alter_post_views_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='blog.post', verbose_name='Запись'),
        ),
    ]
