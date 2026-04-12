from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
	nombre = models.CharField(max_length=80, unique=True)
	prefijo_sku = models.CharField(max_length=5, unique=True)
	activa = models.BooleanField(default=True)

	class Meta:
		db_table = 'categoria'
		ordering = ['nombre']
		verbose_name = 'Categoria'
		verbose_name_plural = 'Categorias'

	def save(self, *args, **kwargs):
		self.nombre = self.nombre.strip().title()
		self.prefijo_sku = self.prefijo_sku.strip().upper()
		super().save(*args, **kwargs)

	def __str__(self):
		return f'{self.nombre} ({self.prefijo_sku})'


class Producto(models.Model):
	nombre = models.CharField(max_length=120)
	descripcion = models.TextField()
	cantidad = models.PositiveIntegerField(validators=[MinValueValidator(0)])
	precio = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))],
	)
	categoria = models.ForeignKey(
		Categoria,
		on_delete=models.PROTECT,
		related_name='productos',
	)
	sku = models.CharField(max_length=30, unique=True)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'producto'
		ordering = ['nombre']
		verbose_name = 'Producto'
		verbose_name_plural = 'Productos'

	@classmethod
	def sugerir_sku(cls, categoria):
		if isinstance(categoria, Categoria):
			categoria_obj = categoria
		else:
			categoria_obj = Categoria.objects.filter(pk=categoria).first()

		prefix = categoria_obj.prefijo_sku if categoria_obj else 'GEN'
		max_number = 0
		for sku in cls.objects.filter(sku__startswith=f'{prefix}-').values_list('sku', flat=True):
			parts = sku.split('-', 1)
			if len(parts) != 2:
				continue
			try:
				number = int(parts[1])
			except ValueError:
				continue
			if number > max_number:
				max_number = number
		return f'{prefix}-{max_number + 1:03d}'

	def save(self, *args, **kwargs):
		self.nombre = self.nombre.strip()
		self.sku = self.sku.strip().upper()
		super().save(*args, **kwargs)

	def __str__(self):
		return f'{self.nombre} ({self.sku})'
