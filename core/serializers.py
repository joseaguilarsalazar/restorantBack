from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Empleado,
    Plato,
    Insumo,
    Mesa,
    Rol,
    Pedido,
    PlatoInsumo,
    CompraInsumo,
)
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = "__all__"

class PlatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plato
        fields = ['id', 'name', 'precio', 'imagen']

class PlatoGetSerializer(serializers.ModelSerializer):
    disponibles = serializers.IntegerField()
    class Meta:
        model = Plato
        fields = ['id', 'name', 'precio', 'imagen', 'disponibles']

    def get_disponibles(self, obj):
        # 🔧 Replace this with your actual logic
        # For example, summing available stock from related items
        platosinsumo = PlatoInsumo.objects.filter(plato__id = self.id)
        disponible = 1000
        for platoinsumo in platosinsumo:
            cantidad = platoinsumo.cantidad / platoinsumo.insumo.stock
            cantidad = int(cantidad)
            if cantidad < disponible:
                disponible = cantidad

        return disponible

class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = "__all__"

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = "__all__"

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = "__all__"

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = "__all__"

class PlatoInsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatoInsumo
        fields = "__all__"

class CompraInsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompraInsumo
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(), write_only=True, source='idRol'
    )
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'rol_id']

    def create(self, validated_data):
        rol = validated_data.pop('idRol')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        Empleado.objects.create(user=user, idRol=rol)
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name

        # Optional: add role name if Empleado exists
        try:
            empleado = Empleado.objects.get(user=self.user)
            data['rol'] = empleado.idRol.name if empleado.idRol else None
        except Empleado.DoesNotExist:
            data['rol'] = None

        return data

