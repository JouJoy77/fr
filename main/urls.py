from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView
from rest_framework import routers
from .views import FullMailingStatAPIView, AllStatAPIView
from .views import ClientViewSet, MessageViewSet, MailingViewSet

#Автоматическая маршрутизация
router = routers.SimpleRouter()
router.register(r'client', ClientViewSet)
router.register(r'message', MessageViewSet)
router.register(r'mailing', MailingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', AllStatAPIView.as_view(), name='all-stats'),
    path('stats/<int:id>', FullMailingStatAPIView.as_view(), name='mailing-stats'),
    # Swagger документация
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]