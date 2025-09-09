from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from Home.models import SiteSettings
import os
from django.conf import settings
import shutil


class Command(BaseCommand):
    help = 'Устанавливает фоновое изображение по умолчанию'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 Установка фонового изображения по умолчанию...'))

        # Получаем или создаем настройки
        site_settings = SiteSettings.get_settings()
        
        if not site_settings.background_image:
            # Путь к исходному изображению в статических файлах
            static_bg_path = os.path.join(settings.BASE_DIR, 'static', 'nlp', 'img', 'bg', 'hero_bg.jpg')
            
            # Проверяем, существует ли файл
            if os.path.exists(static_bg_path):
                # Копируем изображение в медиа папку
                with open(static_bg_path, 'rb') as f:
                    site_settings.background_image.save(
                        'default_background.jpg',
                        ContentFile(f.read()),
                        save=True
                    )
                self.stdout.write(self.style.SUCCESS('✅ Фоновое изображение установлено из статических файлов!'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Файл hero_bg.jpg не найден в статических файлах.'))
                self.stdout.write(self.style.SUCCESS('📝 Но градиентный фон будет отображаться по умолчанию.'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Фоновое изображение уже установлено!'))
            
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('💡 Для смены фонового изображения:'))
        self.stdout.write(self.style.SUCCESS('   1. Перейдите в админку Django (/admin/)'))
        self.stdout.write(self.style.SUCCESS('   2. Откройте "Настройки сайта"'))
        self.stdout.write(self.style.SUCCESS('   3. Загрузите новое фоновое изображение'))