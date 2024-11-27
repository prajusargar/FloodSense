# Generated by Django 5.0.2 on 2024-11-17 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('floodsenseapp', '0004_chatdata_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportedFloodAlertData',
            fields=[
                ('report_id', models.AutoField(primary_key=True, serialize=False)),
                ('topic', models.TextField()),
                ('username', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('MsgText', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
