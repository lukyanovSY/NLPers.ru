"""
Context processors для приложения Home
Обеспечивают доступ к настройкам сайта на всех страницах
"""

from .models import SiteSettings

"""
Context processor для настроек сайта
Добавляет настройки сайта во все шаблоны
"""
def site_settings(request):
    try:
        settings = SiteSettings.get_settings()
        return {
            'site_settings': settings,
            'site_name': settings.site_name,
            'site_description': settings.site_description,
        }
    except Exception as e:
        # Если возникла ошибка, возвращаем значения по умолчанию
        return {
            'site_settings': None,
            'site_name': 'NLPers.ru',
            'site_description': 'Платформа для изучения NLP и искусственного интеллекта',
        }

"""
Context processor для проверки режима обслуживания
"""
def maintenance_check(request):
    try:
        settings = SiteSettings.get_settings()
        return {
            'maintenance_mode': settings.maintenance_mode if settings else False,
        }
    except Exception:
        return {
            'maintenance_mode': False,
        }