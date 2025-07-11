# Generated by Django 5.2 on 2025-06-14 14:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_admin_unidad'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accion',
            options={'ordering': ['nombre'], 'verbose_name': 'Acción', 'verbose_name_plural': 'Acciones'},
        ),
        migrations.AlterModelOptions(
            name='modelopermitido',
            options={'ordering': ['nombre'], 'verbose_name': 'Modelo Permitido', 'verbose_name_plural': 'Modelos Permitidos'},
        ),
        migrations.AlterField(
            model_name='accion',
            name='nombre',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='modelopermitido',
            name='nombre',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterModelTable(
            name='accion',
            table='accion',
        ),
        migrations.AlterModelTable(
            name='modelopermitido',
            table='modelo_permitido',
        ),
        migrations.CreateModel(
            name='PermisoRol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.accion')),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.modelopermitido')),
                ('rol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permisos', to='usuarios.rol')),
            ],
            options={
                'db_table': 'permiso_rol',
                'unique_together': {('rol', 'modelo', 'accion')},
            },
        ),
    ]
