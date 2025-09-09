"""
Команда для оптимизации базы данных
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Оптимизирует базу данных и создает индексы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Анализировать производительность запросов',
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Выполнить VACUUM для SQLite',
        )

    def handle(self, *args, **options):
        self.stdout.write('Начинаем оптимизацию базы данных...')
        
        # Создаем миграции для новых индексов
        self.stdout.write('Создание миграций...')
        call_command('makemigrations')
        
        # Применяем миграции
        self.stdout.write('Применение миграций...')
        call_command('migrate')
        
        # Оптимизация для SQLite
        if 'sqlite' in connection.vendor:
            self.stdout.write('Оптимизация SQLite...')
            with connection.cursor() as cursor:
                # Анализируем базу данных
                cursor.execute('ANALYZE')
                self.stdout.write('✓ Анализ базы данных выполнен')
                
                if options['vacuum']:
                    # Выполняем VACUUM
                    cursor.execute('VACUUM')
                    self.stdout.write('✓ VACUUM выполнен')
                
                # Проверяем целостность
                cursor.execute('PRAGMA integrity_check')
                result = cursor.fetchone()
                if result[0] == 'ok':
                    self.stdout.write('✓ Целостность базы данных проверена')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Проблемы с целостностью: {result[0]}')
                    )
        
        # Собираем статистику
        if options['analyze']:
            self.stdout.write('Сбор статистики...')
            self.analyze_database()
        
        self.stdout.write(
            self.style.SUCCESS('Оптимизация базы данных завершена!')
        )

    def analyze_database(self):
        """Анализирует производительность базы данных"""
        with connection.cursor() as cursor:
            # Получаем информацию о таблицах
            if 'sqlite' in connection.vendor:
                cursor.execute("""
                    SELECT name, sql FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = cursor.fetchall()
                
                self.stdout.write('\nТаблицы в базе данных:')
                for table_name, sql in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    self.stdout.write(f'  {table_name}: {count} записей')
            
            # Получаем информацию об индексах
            if 'sqlite' in connection.vendor:
                cursor.execute("""
                    SELECT name, tbl_name, sql FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                """)
                indexes = cursor.fetchall()
                
                self.stdout.write(f'\nИндексы ({len(indexes)}):')
                for index_name, table_name, sql in indexes:
                    self.stdout.write(f'  {index_name} на {table_name}')
        
        # Анализируем модели Django
        self.stdout.write('\nАнализ моделей Django:')
        from django.apps import apps
        
        for app_config in apps.get_app_configs():
            if app_config.name in ['Home', 'Blog', 'Archive']:
                self.stdout.write(f'\n{app_config.verbose_name}:')
                for model in app_config.get_models():
                    count = model.objects.count()
                    self.stdout.write(f'  {model._meta.verbose_name}: {count} записей')
                    
                    # Показываем индексы модели
                    indexes = model._meta.indexes
                    if indexes:
                        self.stdout.write(f'    Индексы: {len(indexes)}')
                        for index in indexes:
                            fields = ', '.join(index.fields)
                            self.stdout.write(f'      - {fields}')
