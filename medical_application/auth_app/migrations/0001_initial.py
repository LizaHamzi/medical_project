# Generated by Django 4.2.16 on 2024-10-27 15:58

import auth_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('numero_licence', models.CharField(max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to=auth_app.models.upload_to)),
                ('voice_recording', models.FileField(blank=True, null=True, upload_to=auth_app.models.upload_to_voice_doctors)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('ramq', models.CharField(max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to=auth_app.models.upload_to_patients)),
                ('date_naissance', models.DateField(blank=True, null=True, verbose_name='Date de naissance')),
                ('genre', models.CharField(blank=True, choices=[('M', 'Masculin'), ('F', 'Féminin')], max_length=10, null=True)),
                ('ville_naissance', models.CharField(blank=True, max_length=100, null=True, verbose_name='Ville de naissance')),
                ('adresse', models.TextField(blank=True, null=True, verbose_name='Adresse maison')),
                ('telephone', models.CharField(blank=True, max_length=15, null=True)),
                ('voice_recording', models.FileField(blank=True, null=True, upload_to=auth_app.models.upload_to_voice_patients)),
            ],
        ),
    ]
