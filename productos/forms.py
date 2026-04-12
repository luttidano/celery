from django import forms
from django.db.models import Q

from .models import Categoria, Producto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'prefijo_sku', 'activa']
        widgets = {
            'nombre': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Tecnologia'}
            ),
            'prefijo_sku': forms.TextInput(
                attrs={
                    'class': 'form-control text-uppercase',
                    'maxlength': '5',
                    'placeholder': 'Ej: TEC',
                }
            ),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_prefijo_sku(self):
        prefijo = self.cleaned_data['prefijo_sku'].strip().upper()
        if len(prefijo) < 2:
            raise forms.ValidationError('El prefijo debe tener al menos 2 caracteres.')
        return prefijo


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'cantidad', 'precio', 'categoria', 'sku']
        widgets = {
            'nombre': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Descripcion breve del producto',
                }
            ),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'precio': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}
            ),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'sku': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Se genera automaticamente al seleccionar categoria',
                    'readonly': 'readonly',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Categoria.objects.filter(activa=True)
        if self.instance and self.instance.pk and self.instance.categoria_id:
            queryset = Categoria.objects.filter(Q(activa=True) | Q(pk=self.instance.categoria_id))
        self.fields['categoria'].queryset = queryset.order_by('nombre')
        for field in self.fields.values():
            field.required = True
        self.fields['sku'].required = False

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        sku = (cleaned_data.get('sku') or '').strip().upper()

        if not sku and categoria:
            cleaned_data['sku'] = Producto.sugerir_sku(categoria)
            return cleaned_data

        if sku and len(sku) < 4:
            self.add_error('sku', 'El SKU debe tener al menos 4 caracteres.')

        cleaned_data['sku'] = sku
        return cleaned_data
