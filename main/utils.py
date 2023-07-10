# import requests

# from .models import Message, MessageStatus


# def send_message(message, mailing, client):
#     access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjAwMDkzNzgsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6Imh0dHBzOi8vdC5tZS9WbGFkaW1pck9rMSJ9.zm1uj3RE0vQcQRWD-yyDc0xSQMze_okFc1_OiaO4qDM"
#     message_obj = Message.objects.create(mailing=mailing, client=client)
#     message_obj.save()
#     message['id'] = message_obj.id

#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'Content-Type': 'application/json'
#     }

#     # Отправка сообщения на внешний сервис
#     response = requests.post('https://probe.fbrq.cloud/v1/send/{message.id}', json=message, headers=headers)

#     if response.status_code == 200:
#         # Обработка успешной отправки
#         print("Сообщение {id} успешно отправлено")
#         message.status = MessageStatus.SENT
#     else:
#         # Обработка ошибки отправки
#         print("Ошибка отправки сообщения")
#         message.status = MessageStatus.FAILED
