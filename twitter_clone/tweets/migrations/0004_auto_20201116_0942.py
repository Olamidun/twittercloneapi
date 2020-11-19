# Generated by Django 3.1.1 on 2020-11-16 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0003_auto_20201116_0939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='images',
        ),
        migrations.AddField(
            model_name='comments',
            name='file_content',
            field=models.ManyToManyField(related_name='content_file_content', to='tweets.TweetFile'),
        ),
    ]
