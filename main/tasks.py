"""Задачи запускаемые в асинхронном режиме."""

import datetime
import requests
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from fr.celery import app
from .models import Message, Client, Mailing, MessageStatus

import logging
logger = logging.getLogger('trace')


@app.task(bind=True, retry_backoff=True)
def send_message(mailing_id: int, client_id: int):
    """Отправка одного сообщения."""
    mailing = Mailing.objects.get(pk=mailing_id)
    client = Client.objects.get(pk=client_id)

    # Создаем сообщение в базе
    now = timezone.now()
    message_obj = Message.objects.create(mailing=mailing, client=client)
    message_obj.save()
    
    # Доп. задание 11
    client_local_start_time = mailing.get_local_start_time(client.timezone)
    client_local_end_time = mailing.get_local_end_time(client.timezone)
    now = timezone.now()
    if  (client_local_start_time.time()<now.time() or
         now.time() < client_local_end_time.time()):
        message_obj.status = MessageStatus.FAILED
        logger.info(f'MESSAGE:{message_obj.id} MAILING:{mailing.id} CLIENT:{client.id} IS OUTSIDE THE ALLOWED TIME INTERVAL.')
        message_obj.save()
        return

    # Проверки даты
    if now > mailing.end_date_and_time:
        message_obj.status = MessageStatus.FAILED
        logger.info(f'MESSAGE:{message_obj.id} MAILING:{mailing.id} CLIENT:{client.id} EXPIRED.')
    elif now < mailing.start_date_and_time:
        time_diff = int((now - mailing.start_date_and_time).total_seconds())
        logger.info(
            f"Message id: {message_obj.id}, "
            f"It is not time yet, retrying after {time_diff} seconds"
        )
        return self.retry(countdown=time_diff)
    else:
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {settings.TOKEN}'
        }
        message = {
            'id': message_obj.id,
            'phone': int(client.phone_number),
            'text': mailing.text
        }
        try:
            # Запрос
            response = requests.post(
                f'https://probe.fbrq.cloud/v1/send/{message_obj.id}',
                json=message, headers=headers).json()
            if response.status_code == 200:
                # Обработка успешной отправки
                print("Сообщение {message_obj.id} успешно отправлено")
                message_obj.status = MessageStatus.SENT
                logger.info(f'MESSAGE:{message.pk} MAILING:{mailing.id} CLIENT:{client.id} sent successfully.')
            else:
                # Обработка ошибки отправки
                print("Ошибка отправки сообщения {message_obj.id}")
                message_obj.status = MessageStatus.FAILED
                logger.info(f'MESSAGE:{message.pk} MAILING:{mailing.id} CLIENT:{client.id} FAILED.')
        except:
            # Ошибка сети
            print("Ошибка отправки сообщения {message_obj.id}")
            message_obj.status = MessageStatus.FAILED
            logger.info(f'MESSAGE:{message.pk} MAILING:{mailing.id} CLIENT:{client.id} FAILED. NETWORK ERROR')
        finally:
            pass

    message_obj.save()


@app.task
def create_mailing(mailing_id: int, operator_code: int, tag: str):
    """Создаем задачи на отправку сообщений."""
    mailing = Mailing.objects.get(id=mailing_id)

    if timezone.now() >= mailing.start_date_and_time and timezone.now() <= mailing.end_date_and_time:
        mailing.add_client_filter(operator_code=operator_code,
                                  tag=tag)
        clients = Client.objects.filter(mailing.client_filter)
    if not clients:
        logger.info(f'MAILING {mailing.id} CANCELED: NO CLIENTS')
    # Отправка сообщений через внешний сервис
    else:
        for client in clients:
            send_message.delay(mailing.id, client.id)


# Доп. задание 8
@app.task
def send_daily_statistics():
    """Отправка татистики за сутки."""
    yesterday = timezone.now() - datetime.timedelta(days=1)
    data = {
            'mailings_count': Mailing.objects.filter(start_date_and_time>=yesterday).count(),
            'messages_count': Message.objects.filter(created_time>=yesterday, mailing=id).count(),
            'pending': Message.objects.filter(created_time>=yesterday, mailing=id, 
                                              status=MessageStatus.PENDING).count(),
            'failed': Message.objects.filter(created_time>=yesterday, mailing=id, 
                                             status=MessageStatus.FAILED).count(),
            'sent': Message.objects.filter(created_time>=yesterday, mailing=id,
                                           status=MessageStatus.SENT).count(),
        }
    return send_mail(
        f'Daily statistics at {yesterday.date()}',
        f'{data}',
        settings.SERVER_EMAIL,
        [settings.SERVER_EMAIL,],
        fail_silently=False,
    )