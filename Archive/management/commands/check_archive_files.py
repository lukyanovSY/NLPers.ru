from django.core.management.base import BaseCommand
from Archive.models import ArchiveFile


class Command(BaseCommand):
    help = 'Проверяет и исправляет файлы архива'

    def handle(self, *args, **options):
        self.stdout.write('Проверка файлов архива...')
        
        # Получаем все файлы
        files = ArchiveFile.objects.all()
        
        self.stdout.write(f'Всего файлов в базе: {files.count()}')
        
        # Проверяем файлы без связанных файлов
        files_without_file = []
        for file in files:
            if not file.file:
                files_without_file.append(file)
        
        if files_without_file:
            self.stdout.write(
                self.style.WARNING(
                    f'Найдено {len(files_without_file)} файлов без связанных файлов:'
                )
            )
            for file in files_without_file:
                self.stdout.write(f'  - {file.title} (ID: {file.pk})')
            
            # Удаляем файлы без связанных файлов
            response = input('Удалить файлы без связанных файлов? (y/n): ')
            if response.lower() == 'y':
                for file in files_without_file:
                    file.delete()
                self.stdout.write(
                    self.style.SUCCESS('Файлы без связанных файлов удалены')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('Все файлы имеют связанные файлы')
            )
        
        # Показываем статистику
        total_files = ArchiveFile.objects.count()
        public_files = ArchiveFile.objects.filter(is_public=True).count()
        
        self.stdout.write(f'Всего файлов: {total_files}')
        self.stdout.write(f'Публичных файлов: {public_files}')
        
        self.stdout.write(
            self.style.SUCCESS('Проверка завершена')
        ) 