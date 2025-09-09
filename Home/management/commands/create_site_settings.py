from django.core.management.base import BaseCommand
from Home.models import SiteSettings


class Command(BaseCommand):
    help = 'Создает базовые настройки сайта'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Создание базовых настроек сайта...'))

        # Создаем или получаем настройки
        settings = SiteSettings.get_settings()
        
        if settings:
            self.stdout.write(self.style.SUCCESS('✅ Настройки сайта созданы/обновлены!'))
            self.stdout.write(self.style.SUCCESS(f'📝 Название сайта: {settings.site_name}'))
            self.stdout.write(self.style.SUCCESS(f'📄 Описание: {settings.site_description}'))
            self.stdout.write(self.style.SUCCESS(''))
            self.stdout.write(self.style.WARNING('💡 Для настройки фонового изображения и других параметров:'))
            self.stdout.write(self.style.WARNING('   1. Перейдите в админку Django'))
            self.stdout.write(self.style.WARNING('   2. Найдите раздел "Настройки сайта"'))
            self.stdout.write(self.style.WARNING('   3. Загрузите фоновое изображение и настройте другие параметры'))
        else:
            self.stdout.write(self.style.ERROR('❌ Ошибка при создании настроек!'))