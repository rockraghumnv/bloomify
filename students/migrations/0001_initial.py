# Generated by Django 5.2.1 on 2025-05-17 17:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teachers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remember_score', models.FloatField(default=0.0)),
                ('understand_score', models.FloatField(default=0.0)),
                ('apply_score', models.FloatField(default=0.0)),
                ('analyze_score', models.FloatField(default=0.0)),
                ('evaluate_score', models.FloatField(default=0.0)),
                ('create_score', models.FloatField(default=0.0)),
                ('overall_score', models.FloatField(default=0.0)),
                ('feedback_text', models.TextField()),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.quiz')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'quiz')},
            },
        ),
        migrations.CreateModel(
            name='StudentResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_answer', models.CharField(max_length=200)),
                ('is_correct', models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.question')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.quiz')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'quiz', 'question')},
            },
        ),
    ]
