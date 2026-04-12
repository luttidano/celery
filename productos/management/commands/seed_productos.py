from decimal import Decimal

from django.core.management.base import BaseCommand

from productos.models import Categoria, Producto

CATEGORIAS_SEED = [
    {'nombre': 'Tecnologia', 'prefijo_sku': 'TEC', 'activa': True},
    {'nombre': 'Oficina', 'prefijo_sku': 'OFI', 'activa': True},
    {'nombre': 'Hogar', 'prefijo_sku': 'HOG', 'activa': True},
    {'nombre': 'Alimentos', 'prefijo_sku': 'ALI', 'activa': True},
    {'nombre': 'Otros', 'prefijo_sku': 'OTR', 'activa': True},
]

SEED_DATA = [
    {
        'sku': 'TEC-001',
        'nombre': 'Laptop empresarial',
        'descripcion': 'Laptop de 14 pulgadas para trabajo administrativo.',
        'cantidad': 10,
        'precio': Decimal('899990.00'),
        'categoria': 'Tecnologia',
    },
    {
        'sku': 'TEC-002',
        'nombre': 'Mouse inalambrico',
        'descripcion': 'Mouse optico con conexion USB.',
        'cantidad': 45,
        'precio': Decimal('12990.00'),
        'categoria': 'Tecnologia',
    },
    {
        'sku': 'OFI-001',
        'nombre': 'Resma papel carta',
        'descripcion': 'Resma de 500 hojas tamano carta.',
        'cantidad': 80,
        'precio': Decimal('4990.00'),
        'categoria': 'Oficina',
    },
    {
        'sku': 'OFI-002',
        'nombre': 'Silla ergonomica',
        'descripcion': 'Silla de oficina con soporte lumbar.',
        'cantidad': 12,
        'precio': Decimal('159990.00'),
        'categoria': 'Oficina',
    },
    {
        'sku': 'HOG-001',
        'nombre': 'Lampara LED',
        'descripcion': 'Lampara de escritorio con luz regulable.',
        'cantidad': 24,
        'precio': Decimal('24990.00'),
        'categoria': 'Hogar',
    },
    {
        'sku': 'ALI-001',
        'nombre': 'Agua mineral 500ml',
        'descripcion': 'Pack de 12 botellas de agua mineral.',
        'cantidad': 30,
        'precio': Decimal('6990.00'),
        'categoria': 'Alimentos',
    },
]


class Command(BaseCommand):
    help = 'Puebla la tabla productos con datos de ejemplo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina productos existentes antes de insertar datos semilla.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            Producto.objects.all().delete()
            self.stdout.write(self.style.WARNING('Registros previos eliminados.'))

        categorias_map = {}
        for categoria_data in CATEGORIAS_SEED:
            categoria, _ = Categoria.objects.update_or_create(
                nombre=categoria_data['nombre'],
                defaults=categoria_data,
            )
            categorias_map[categoria.nombre] = categoria

        created = 0
        updated = 0

        for data in SEED_DATA:
            categoria = categorias_map[data['categoria']]
            defaults = {
                'nombre': data['nombre'],
                'descripcion': data['descripcion'],
                'cantidad': data['cantidad'],
                'precio': data['precio'],
                'categoria': categoria,
            }
            _, was_created = Producto.objects.update_or_create(
                sku=data['sku'],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeder completado. Creados: {created} | Actualizados: {updated}'
            )
        )
