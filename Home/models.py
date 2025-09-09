from django.db import models
from django.core.exceptions import ValidationError

"""Настройки сайта"""
class SiteSettings(models.Model):
    site_name = models.CharField(
        max_length=100, 
        default='NLPers.ru',
        verbose_name='Название сайта'
    )
    site_description = models.TextField(
        blank=True,
        verbose_name='Описание сайта',
        help_text='Краткое описание сайта для SEO'
    )
    background_image = models.ImageField(
        upload_to='site_backgrounds/',
        blank=True,
        null=True,
        verbose_name='Фоновое изображение',
        help_text='Основное фоновое изображение сайта'
    )
    background_overlay_opacity = models.FloatField(
        default=0.7,
        verbose_name='Прозрачность наложения',
        help_text='От 0.0 (полностью прозрачно) до 1.0 (полностью непрозрачно)'
    )
    header_background_color = models.CharField(
        max_length=7,
        default='#1a1a1a',
        verbose_name='Цвет фона шапки',
        help_text='HEX цвет для фона меню'
    )
    logo = models.ImageField(
        upload_to='site_logos/',
        blank=True,
        null=True,
        verbose_name='Логотип сайта'
    )
    favicon = models.ImageField(
        upload_to='site_favicons/',
        blank=True,
        null=True,
        verbose_name='Favicon',
        help_text='Иконка сайта (16x16 или 32x32 пикселя)'
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name='Email для связи'
    )
    social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Социальные сети',
        help_text='Ссылки на соцсети в формате JSON'
    )
    analytics_code = models.TextField(
        blank=True,
        verbose_name='Код аналитики',
        help_text='Google Analytics, Яндекс.Метрика и т.д.'
    )
    maintenance_mode = models.BooleanField(
        default=False,
        verbose_name='Режим обслуживания',
        help_text='Включить для технических работ'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return f'Настройки сайта - {self.site_name}'

    def clean(self):
        # Проверяем диапазон прозрачности
        if not (0.0 <= self.background_overlay_opacity <= 1.0):
            raise ValidationError('Прозрачность должна быть между 0.0 и 1.0')

    def save(self, *args, **kwargs):
        # Убеждаемся, что существует только одна запись настроек
        if not self.pk and SiteSettings.objects.exists():
            # Если это новая запись и настройки уже существуют,
            # обновляем существующую запись
            existing = SiteSettings.objects.first()
            existing.site_name = self.site_name
            existing.site_description = self.site_description
            existing.background_image = self.background_image
            existing.background_overlay_opacity = self.background_overlay_opacity
            existing.header_background_color = self.header_background_color
            existing.logo = self.logo
            existing.favicon = self.favicon
            existing.contact_email = self.contact_email
            existing.social_links = self.social_links
            existing.analytics_code = self.analytics_code
            existing.maintenance_mode = self.maintenance_mode
            existing.save()
            return existing
        super().save(*args, **kwargs)
        
    """Получить настройки сайта (или создать по умолчанию)"""
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'NLPers.ru',
                'site_description': 'Платформа для изучения NLP и искусственного интеллекта',
                'background_overlay_opacity': 0.7,
                'header_background_color': '#1a1a1a',
                'social_links': {
                    'twitter': '',
                    'facebook': '',
                    'instagram': '',
                    'youtube': '',
                    'telegram': ''
                }
            }
        )
        return settings
