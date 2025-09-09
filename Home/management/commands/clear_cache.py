"""
Команда для очистки кэша
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Очищает весь кэш приложения'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pattern',
            type=str,
            help='Паттерн для очистки определенных ключей кэша',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Очистить весь кэш',
        )

    def handle(self, *args, **options):
        if options['all']:
            # Очищаем весь кэш
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('Весь кэш успешно очищен')
            )
        elif options['pattern']:
            # Очищаем кэш по паттерну
            pattern = options['pattern']
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
                self.stdout.write(
                    self.style.SUCCESS(f'Кэш с паттерном "{pattern}" очищен')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Текущий бэкенд кэша не поддерживает удаление по паттерну')
                )
        else:
            # Очищаем основные ключи кэша
            cache_keys_to_clear = [
                'posts_list_*',
                'popular_posts_*',
                'recent_posts_*',
                'categories_with_counts',
                'tags_with_counts',
                'files_list_*',
                'featured_files_*',
                'recent_files_*',
                'popular_files_*',
                'file_categories',
                'file_statistics',
            ]
            
            cleared_count = 0
            for key_pattern in cache_keys_to_clear:
                if hasattr(cache, 'delete_pattern'):
                    cache.delete_pattern(key_pattern)
                    cleared_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Очищено {cleared_count} паттернов кэша')
            )
        
        # Показываем информацию о кэше
        self.stdout.write('\nИнформация о кэше:')
        self.stdout.write(f'Бэкенд: {settings.CACHES["default"]["BACKEND"]}')
        self.stdout.write(f'Локация: {settings.CACHES["default"]["LOCATION"]}')
        self.stdout.write(f'Префикс: {settings.CACHES["default"]["KEY_PREFIX"]}')
        self.stdout.write(f'Таймаут: {settings.CACHES["default"]["TIMEOUT"]} секунд')
