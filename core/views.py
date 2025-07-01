from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import *
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.db import transaction

class RolViewSet(ModelViewSet):
    serializer_class = RolSerializer
    queryset = Rol.objects.all()

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().filter(is_superuser=False)

class EmpleadoViewSet(ModelViewSet):
    serializer_class = EmpleadoSerializer
    queryset = Empleado.objects.all()

class MesaViewSet(ModelViewSet):
    serializer_class = MesaSerializer
    queryset = Mesa.objects.all()

class PlatoViewSet(ModelViewSet):
    queryset = Plato.objects.all()
    serializer_class = PlatoSerializer

    @swagger_auto_schema(
        operation_description="Create a new Plato. Must use multipart/form-data for image upload.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'precio'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'precio': openapi.Schema(type=openapi.TYPE_INTEGER),
                'imagen': openapi.Schema(type=openapi.TYPE_FILE, description="Image file (optional)"),
            },
        ),
        consumes=['multipart/form-data'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class PedidoViewSet(ModelViewSet):
    serializer_class = PedidoSerializer
    queryset = Pedido.objects.all()

    def create(self, request, *args, **kwargs):
        plato_id = request.data.get('plato')
        cantidad = int(request.data.get('cantidad'))
        plato = Plato.objects.filter(id=plato_id).first()

        if not plato:
            return Response({"error": "Plato no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        insumos = PlatoInsumo.objects.filter(plato=plato)

        try:
            with transaction.atomic():
                for pi in insumos:
                    insumo = pi.insumo
                    if insumo.stock < pi.cantidad * cantidad:
                        raise ValueError(f"Insumo {insumo.nombre} sin stock suficiente.")
                    insumo.stock -= pi.cantidad * cantidad
                    insumo.save()

                # Guardar el pedido solo si los insumos fueron descontados correctamente
                return super().create(request, *args, **kwargs)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PlatoInsumoViewSet(ModelViewSet):
    serializer_class = PlatoInsumoSerializer
    queryset = PlatoInsumo.objects.all()

class CompraInsumoViewSet(ModelViewSet):
    serializer_class = CompraInsumoSerializer
    queryset = CompraInsumo.objects.all()

class InsumoViewSet(ModelViewSet):
    serializer_class = InsumoSerializer
    queryset = Insumo.objects.all()


class RegisterView(APIView):
    """
    Register a new user, create an associated Empleado with a selected Rol.
    """

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response("User registered successfully."),
            400: "Invalid input or validation error"
        },
        operation_description="Registers a new user and assigns them a role. "
                              "This will also create an Empleado instance linked to the user.",
        operation_summary="User Registration"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Obtain a JWT access and refresh token pair. Also returns basic user info and role if available.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="JWT token response with user info",
                examples={
                    "application/json": {
                        "refresh": "your-refresh-token",
                        "access": "your-access-token",
                        "user_id": 1,
                        "username": "jose",
                        "first_name": "José",
                        "last_name": "Aguilar",
                        "rol": "Administrador"
                    }
                }
            ),
            401: "Invalid credentials"
        },
        operation_description="Authenticates user credentials and returns JWT tokens and user info.",
        operation_summary="User Login with JWT"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Change password (JWT required)",
        operation_description=(
            "Change password for the currently authenticated user. "
            "You must send the access token in the `Authorization` header like this:\n\n"
            "`Authorization: Bearer <access_token>`"
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["current_password", "new_password"],
            properties={
                "current_password": openapi.Schema(type=openapi.TYPE_STRING, example="old_password"),
                "new_password": openapi.Schema(type=openapi.TYPE_STRING, example="new_password123"),
            },
        ),
        responses={
            200: openapi.Response(description="Password changed successfully."),
            400: openapi.Response(description="Invalid input or incorrect current password."),
            401: openapi.Response(description="Authentication credentials were not provided or invalid."),
        },
    )
    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response({"error": "Both current and new passwords are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"success": "Password changed successfully."}, status=status.HTTP_200_OK)
    

class WebSocketDocView(APIView):
    """
    Documentación del WebSocket.

    URL del WebSocket: `ws://lp5-backend.jmtqu4.easypanel.host/ws/pedidos/`

    ▶️ Al conectarse:
    - El cliente se une al grupo `realtime_updates`.

    📤 Datos que recibirá el cliente:
    ```json
    {
        "type": "send_data",
        "data": [
            {
                "id": 1,
                "mesa": 3,
                "plato": "Arroz con pollo",
                "cantidad": 2,
                "datetime": "2025-06-17T19:38:51.123Z",
                "estado": "ordenado"
            },
            ...
        ]
    }
    ```
    """

    @swagger_auto_schema(
        operation_summary="Documentación del WebSocket de pedidos",
        operation_description="""
Documentación del WebSocket.

    URL del WebSocket: `wss://lp5-backend.jmtqu4.easypanel.host/ws/pedidos/`

    ▶️ Al conectarse:
    - El cliente se une al grupo `realtime_updates`.

    📤 Datos que recibirá el cliente:
    ```json
    {
        "type": "send_data",
        "data": [
            {
                "id": 1,
                "mesa": 3,
                "plato": "Arroz con pollo",
                "cantidad": 2,
                "datetime": "2025-06-17T19:38:51.123Z",
                "estado": "ordenado"
            },
            ...
        ]
    }
    ```
        """,
        responses={200: "OK"}
    )
    def get(self, request):
        return Response({"detail": "Esta vista es solo para documentación"}, status=status.HTTP_200_OK)

    
class PedidoToNextStateAPIView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Cambiar estado del pedido al siguiente",
        operation_description="""
Avanza el estado de un pedido en la secuencia:

`ordenado → preparacion → servido → pagado`

Requiere el ID del pedido en el cuerpo de la solicitud.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["pedido_id"],
            properties={
                "pedido_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del pedido"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Estado cambiado con éxito",
                examples={
                    "application/json": {
                        "success": "Estado actualizado correctamente",
                        "nuevo_estado": "preparacion"
                    }
                },
            ),
            404: openapi.Response(
                description="Pedido no encontrado",
                examples={
                    "application/json": {
                        "error": "Pedido no encontrado"
                    }
                },
            ),
            400: openapi.Response(
                description="No se puede avanzar el estado",
                examples={
                    "application/json": {
                        "error": "El pedido ya está en su estado final o el estado actual es inválido"
                    }
                },
            ),
        }
    )
    def post(self, request):
        pedido_id = request.data.get('pedido_id')

        pedido = Pedido.objects.filter(id=pedido_id).first()
        if not pedido:
            return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        TRANSICIONES = {
            'ordenado': 'preparacion',
            'preparacion': 'servido',
            'servido': 'pagado',
        }

        nuevo_estado = TRANSICIONES.get(pedido.estado)
        if not nuevo_estado:
            return Response({'error': 'El pedido ya está en su estado final o el estado actual es inválido'}, status=status.HTTP_400_BAD_REQUEST)

        pedido.estado = nuevo_estado
        pedido.save()

        return Response({
            'success': 'Estado actualizado correctamente',
            'nuevo_estado': nuevo_estado
        }, status=status.HTTP_200_OK)