from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('academico', '0005_remove_campus_infraestructura_compartida'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unidadcurricular',
            name='horas_semanales',
        ),
    ]
