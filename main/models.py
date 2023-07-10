from datetime import date, time, datetime
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import pytz

class AllowedTimeInterval(models.Model):
    """Вспомогательный класс интервала времени."""
    default_min_time = time(hour=10)
    default_max_time = time(hour=20)
    min_time = models.DateTimeField(verbose_name='Минимальное допустимое время рассылки',
                                    default=datetime.combine(date.today(), default_min_time))
    max_time = models.DateTimeField(verbose_name='Максимальное допустимое время рассылки',
                                    default=datetime.combine(date.today(), default_max_time))

class Mailing(models.Model):
    """Модель рассылки."""
    id = models.AutoField(verbose_name='ID рассылки', primary_key=True)
    start_date_and_time = models.DateTimeField(verbose_name='Дата и время начала рассылки')
    text = models.TextField(verbose_name='Текст для отправки клиенту')
    # Фильтр свойств клиентов, на которых должна быть произведена рассылка
    client_filter = models.Q()
    filter_code = models.CharField(null=True, blank=True,
                                   max_length=3,verbose_name='Фильтр кода оператора')
    filter_tag = models.CharField(null=True, blank=True,
                                  max_length=200, verbose_name='Фильтр тега')
    end_date_and_time = models.DateTimeField(verbose_name='Дата и время окончания рассылки')
    time_interval = models.ForeignKey(to=AllowedTimeInterval, 
                                      verbose_name='Промежуток времени для отправки', blank=True,
                                      on_delete=models.CASCADE, default=None, null=True)

    def add_client_filter(self, operator_code=None, tag=None):
        oper_code = operator_code or self.filter_code
        tag_filter = tag or self.filter_tag
        if operator_code:
            self.client_filter &= models.Q(client__operator_code=oper_code)
        if tag:
            self.client_filter &= models.Q(client__tags__in=tag_filter)
    
    def get_local_start_time(self, client_timezone):
        tz = pytz.timezone(client_timezone)
        return self.start_date_and_time.astimezone(tz)
    
    def get_local_end_time(self, client_timezone):
        tz = pytz.timezone(client_timezone)
        return self.end_date_and_time.astimezone(tz)

    def __str__(self):
        return f'{self.id} Start: {self.start_date_and_time} End: {self.end_date_and_time}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

class Client(models.Model):
    """Модель клиента."""
    phone_validator = RegexValidator(
        regex=r'^7\d{10}$',
        message="Номер телефона (в формате 7XXXXXXXXXX, где X - цифра от 0 до 9)")
    
    id = models.AutoField(verbose_name='ID клиента', primary_key=True)
    phone_number = models.CharField(
        validators=[phone_validator,], max_length=11, unique=True,
        verbose_name='Номер телефона')
    operator_code = models.CharField(max_length=3, verbose_name='Код оператора')
    tag = models.CharField(max_length=200, verbose_name='Тег')
    timezone = models.CharField(max_length=255, choices=[(tz, tz) for tz in pytz.all_timezones])
    
    def __str__(self):
        return f'{self.id}, {self.phone_number}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class MessageStatus(models.TextChoices):
    """Вспомогательный класс статуса."""
    PENDING = 'PENDING', 'Ожидает отправки'
    SENT = 'SENT', 'Отправлено'
    FAILED = 'FAILED', 'Не удалось доставить'

class Message(models.Model):
    """Модель сообщений."""
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(verbose_name='Время создания')
    status = models.CharField(verbose_name='Статус отправки',
                              max_length=10,
                              choices=MessageStatus.choices,
                              default=MessageStatus.PENDING)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE,verbose_name='Рассылка')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self) -> str:
        return f'{self.id}, Статус: {self.status}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Message, self).save(*args, **kwargs)
    
    