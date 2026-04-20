from django.db import migrations


def populate_teachers(apps, schema_editor):
    Classroom = apps.get_model('classrooms', 'Classroom')
    for classroom in Classroom.objects.all().iterator():
        if classroom.teacher_id:
            classroom.teachers.add(classroom.teacher_id)


def unpopulate_teachers(apps, schema_editor):
    Classroom = apps.get_model('classrooms', 'Classroom')
    through_model = Classroom.teachers.through
    through_model.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('classrooms', '0008_classroom_teachers_alter_classroom_teacher'),
    ]

    operations = [
        migrations.RunPython(populate_teachers, unpopulate_teachers),
    ]
