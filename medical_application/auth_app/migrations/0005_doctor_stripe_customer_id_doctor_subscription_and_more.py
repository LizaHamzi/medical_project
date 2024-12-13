# Generated by Django 4.2.16 on 2024-12-06 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0004_conversation_remove_chatsession_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='doctor',
            name='subscription',
            field=models.CharField(choices=[('basic', 'Basic'), ('pro', 'Pro'), ('enterprise', 'Enterprise')], default='basic', max_length=20),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='chatsession',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
