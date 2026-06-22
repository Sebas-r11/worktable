# Generated manually for P1 audit — unique metric per assignment

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metricas', '0002_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='metricaeficiencia',
            constraint=models.UniqueConstraint(
                condition=models.Q(('asignacion__isnull', False)),
                fields=('asignacion',),
                name='unique_metrica_por_asignacion',
            ),
        ),
    ]
