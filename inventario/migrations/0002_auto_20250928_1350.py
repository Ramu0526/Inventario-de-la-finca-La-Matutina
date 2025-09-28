# inventario/migrations/000X_...py (tu nuevo archivo vacío)

from django.db import migrations, connection

# Lista de campos que queremos asegurar que existan en el modelo Ganado
# (nombre_del_campo, tipo_de_dato_sql)
CAMPOS_A_VERIFICAR = [
    ('fecha_fallecimiento', 'date'),
    ('razon_fallecimiento', 'text'),
    ('fecha_venta', 'date'),
    ('valor_venta', 'numeric(10, 2)'),
    ('razon_venta', 'text'),
    ('comprador', 'varchar(100)'),
    ('comprador_telefono', 'varchar(20)'),
]

def add_missing_ganado_fields(apps, schema_editor):
    """
    Esta función revisa qué columnas faltan en la tabla inventario_ganado y las añade.
    """
    table_name = 'inventario_ganado'

    # Usamos el cursor de la base de datos para interactuar directamente
    with connection.cursor() as cursor:
        # Obtenemos la lista de columnas que ya existen en la tabla
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]

        # Recorremos la lista de campos que deberían existir
        for field_name, field_type in CAMPOS_A_VERIFICAR:
            # Si el campo NO está en la lista de columnas existentes...
            if field_name not in existing_columns:
                print(f"  -> Añadiendo columna faltante: {field_name}")
                # ...lo añadimos usando SQL directamente.
                cursor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{field_name}" {field_type}')
            else:
                print(f"  -> La columna ya existe: {field_name} (omitido)")

class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        # Esta operación especial ejecuta nuestra función de Python
        migrations.RunPython(add_missing_ganado_fields, reverse_code=migrations.RunPython.noop),
    ]