from django.shortcuts import render
from .models import Client, Mailing, Message
from django.utils import timezone
from fr.serializers import ClientSerializer, MailingSerializer, MessageSerializer
# from .utils import send_message
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Client, Message, Mailing, MessageStatus

import logging
logger = logging.getLogger('trace')


@extend_schema_view(
    list=extend_schema(summary='Список всех клиентов'),
    create=extend_schema(summary='Создание клиента'),
    retrieve=extend_schema(summary='Детальные данные клиента'),
    update=extend_schema(summary='Создание/изменение клиента'),
    partial_update=extend_schema(summary='Изменение клиента'),
    destroy=extend_schema(summary='Удаление клиента'),)
class ClientViewSet(viewsets.ModelViewSet):
    """Клиенты."""

    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def perform_create(self, serializer):
        client = serializer.save()
        logger.info(f'CLIENT:{client.id} created.')

    def perform_update(self, serializer):
        client = serializer.save()
        logger.info(f'CLIENT:{client.id} updated.')

    def perform_destroy(self, serializer):
        logger.info(f'CLIENT:{serializer.id} deleted.')
        serializer.delete()


@extend_schema_view(
    list=extend_schema(summary='Список всех сообщений'),)
class MessageViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """Список всех сообщений."""

    queryset = Message.objects.all()
    serializer_class = MessageSerializer


@extend_schema_view(
    list=extend_schema(summary='Список всех рассылок'),
    create=extend_schema(summary='Создание рассылки'),
    retrieve=extend_schema(summary='Детальные данные по рассылке'),
    update=extend_schema(summary='Создание/изменение рассылки'),
    partial_update=extend_schema(summary='Изменение рассылки'),
    destroy=extend_schema(summary='Удаление рассылки'),)
class MailingViewSet(viewsets.ModelViewSet):
    """Рассылки."""

    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer

    def perform_create(self, serializer):
        serializer.save()
        return Response(
            {'mailing': 'created'},
            status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        d = serializer.save()
        logger.info(f'Mailing:{d.id} updated.')

    def perform_destroy(self, serializer):
        logger.info(f'Mailing:{serializer.id} deleted.')
        serializer.delete()


@extend_schema_view(
    get=extend_schema(summary='Статистика по рассылке'),)
class FullMailingStatAPIView(APIView):
    """Детальная статистика по выбранной рассылке."""

    def get(self, request, id):
        try:
            mailing = Mailing.objects.all().get(pk=id)
        except ObjectDoesNotExist:
            data = {
                'message': f'Mailing {id} does not exist',
            }
        else:
            clients_count = Client.objects.filter(mailing.client_filter).count()
            data = {
                'mailing': id,
                'clients_count': clients_count,
                'messages_count': Message.objects.filter(mailing=id).count(),
                'pending': Message.objects.filter(mailing=id, status=MessageStatus.PENDING).count(),
                'failed': Message.objects.filter(mailing=id, status=MessageStatus.FAILED).count(),
                'sent': Message.objects.filter(mailing=id, status=MessageStatus.SENT).count(),
                'start_date': mailing.start_date_and_time,
                'end_date': mailing.end_date_and_time
            }
        finally:
            return Response(data)


@extend_schema_view(
    get=extend_schema(summary='Общая статистика'),)
class AllStatAPIView(APIView):
    """Общая статистика по работе сервиса."""

    def get(self, request, id):
        data = {
            'mailings_count': Mailing.objects.all().count(),
            'clients_count': Client.objects.all().count(),
            'messages_count': Message.objects.filter(mailing=id).count(),
            'pending': Message.objects.filter(mailing=id, status=MessageStatus.PENDING).count(),
            'failed': Message.objects.filter(mailing=id, status=MessageStatus.FAILED).count(),
            'sent': Message.objects.filter(mailing=id, status=MessageStatus.SENT).count(),
        }
        return Response(data)


# Логика создания рассылки
# def create_mailing(request):
#     mailing_id = request.get('id')
#     mailing = Mailing.objects.get(id=mailing_id)

#     if timezone.now() >= mailing.start_date_and_time and timezone.now() <= mailing.end_date_and_time:
#         mailing.add_client_filter(operator_code=request.get('operator_code'),
#                                   tag=request.get('tag'))
#         clients = Client.objects.filter(mailing.client_filter)
#     # Отправка сообщений через внешний сервис
#     for client in clients:
#         message = {
#             'id': request.get('id'),
#             'phone': int(client.phone_number),
#             'text': request.get('text'),
#         }
#         send_message(message, mailing, client)
