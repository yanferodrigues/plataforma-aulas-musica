from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonprogress',
            name='resume_position',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
