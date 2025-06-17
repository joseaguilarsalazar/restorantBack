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