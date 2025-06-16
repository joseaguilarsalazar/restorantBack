from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmpleadoViewSet,
    RolViewSet,
    MesaViewSet,
    PlatoViewSet,
    PlatoInsumoViewSet,
    PedidoViewSet,
    InsumoViewSet,
    CompraInsumoViewSet,
    RegisterView,  # ✅ Add this
    CustomTokenObtainPairView,  # ✅ Optional: only if using custom login response
    UserViewSet,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r'empleados', EmpleadoViewSet)
router.register(r'roles', RolViewSet)
router.register(r'mesas', MesaViewSet)
router.register(r'platos', PlatoViewSet)
router.register(r'plato-insumos', PlatoInsumoViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'insumos', InsumoViewSet)
router.register(r'compras-insumo', CompraInsumoViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # ✅ JWT authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # or TokenObtainPairView
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
