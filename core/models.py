from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Rol(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)

class Empleado(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idRol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.user.first_name + ' ' + self.user.last_name)

class Mesa(models.Model):
    pass

    def __str__(self):
        return str(self.id)
    
class Plato(models.Model):
    name = models.CharField(max_length=100)
    precio = models.IntegerField()
    imagen = models.ImageField(upload_to='platos/', blank=True, null=True)

    def __str__(self):
        return str(self.name)

class Pedido(models.Model):
    plato = models.ForeignKey(Plato, on_delete=models.SET_NULL, null=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    ESTADO_CHOICES = [
        ('ordenado', 'Ordenado'),
        ('preparacion', 'En Preparación'),
        ('servido', 'Servido'),
        ('pagado', 'Pagado'),
    ]

    estado = models.CharField(
        max_length=100,
        choices=ESTADO_CHOICES,
        default='ordenado',  # optional default
    )

    def __str__(self):
        return str('Pedido' + str(self.id))
    
class Insumo(models.Model):
    name = models.CharField(max_length=100)
    stock = models.FloatField()
    precio = models.FloatField()
    unidadMedida = models.CharField(max_length=100)

class PlatoInsumo(models.Model):
    plato = models.ForeignKey(Plato, on_delete= models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete= models.SET_NULL, null=True)
    cantidad = models.FloatField()

class CompraInsumo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    insumo = models.ForeignKey(Insumo, on_delete= models.SET_NULL, null=True)
    cantidad = models.FloatField()
    fecha = models.DateTimeField(default=timezone.now)