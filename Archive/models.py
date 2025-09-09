from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import os

# Импортируем Tag из Blog для связи
try:
    from Blog.models import Tag
except ImportError:
    Tag = None


class FileCategory(models.Model):
    """Модель категорий для файлов архива"""
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)
    color = models.CharField('Цвет', max_length=7, default='#007bff', help_text='HEX цвет для отображения')
    icon = models.CharField('Иконка', max_length=50, blank=True, help_text='CSS класс Font Awesome')
    image = models.ImageField('Картинка', upload_to='archive/categories/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Категория файлов'
        verbose_name_plural = 'Категории файлов'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.create_slug(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('Archive:category_detail', kwargs={'pk': self.pk})
    
    @property
    def files_count(self):
        return self.files.filter(is_public=True).count()
    
    def create_slug(self, name):
        """Создает slug с транслитерацией русского текста"""
        import re
        import uuid
        
        # Расширенный словарь для транслитерации
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        }
        
        # Транслитерируем
        result = ''
        for char in name.lower():
            if char in translit_dict:
                result += translit_dict[char]
            else:
                result += char
        
        # Очищаем и форматируем slug
        slug = result.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Если slug пустой, создаем случайный
        if not slug:
            slug = f'file-category-{uuid.uuid4().hex[:8]}'
        
        # Проверяем уникальность
        counter = 1
        original_slug = slug
        while FileCategory.objects.filter(slug=slug).exclude(id=self.id if self.id else None).exists():
            slug = f'{original_slug}-{counter}'
            counter += 1
        
        return slug


class ArchiveFile(models.Model):
    """Модель файлов архива"""
    FILE_TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('audio', 'Аудио'),
        ('document', 'Документ'),
        ('archive', 'Архив'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    description = models.TextField('Описание', blank=True)
    file = models.FileField('Файл', upload_to='archive/files/')
    thumbnail = models.ImageField('Превью', upload_to='archive/thumbnails/', blank=True, null=True, help_text='Изображение для превью файла')
    file_type = models.CharField('Тип файла', max_length=10, choices=FILE_TYPE_CHOICES)
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='files', verbose_name='Категория')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files', verbose_name='Загрузил')
    
    # Теги
    tags = models.CharField('Теги', max_length=200, blank=True, help_text='Разделяйте теги запятыми')
    tag_objects = models.ManyToManyField(Tag, blank=True, related_name='archive_files', verbose_name='Теги')
    
    # Статистика
    downloads_count = models.PositiveIntegerField('Количество скачиваний', default=0)
    views_count = models.PositiveIntegerField('Количество просмотров', default=0)
    likes_count = models.PositiveIntegerField('Количество лайков', default=0)
    
    # Настройки
    is_public = models.BooleanField('Публичный', default=True)
    is_featured = models.BooleanField('Рекомендуемый', default=False)
    allow_comments = models.BooleanField('Разрешить комментарии', default=True)
    
    # Даты
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Файл архива'
        verbose_name_plural = 'Файлы архива'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.create_slug(self.title)
        
        # Синхронизируем теги
        super().save(*args, **kwargs)
        if self.tags:
            self.sync_tags_from_string()
    
    def get_absolute_url(self):
        return reverse('Archive:file_detail', kwargs={'pk': self.pk})
    
    def get_tags_list(self):
        """Возвращает список тегов как строки"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_tag_objects(self):
        """Возвращает объекты тегов"""
        return self.tag_objects.filter(is_active=True)
    
    def sync_tags_from_string(self):
        """Синхронизирует теги из строки с объектами Tag"""
        if not self.tags or not Tag:
            return
        
        tag_names = self.get_tags_list()
        tag_objects = []
        
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.strip(),
                defaults={'slug': Tag().create_slug(tag_name.strip())}
            )
            tag_objects.append(tag)
        
        self.tag_objects.set(tag_objects)
    
    def sync_tags_to_string(self):
        """Синхронизирует объекты тегов в строку"""
        tag_names = [tag.name for tag in self.get_tag_objects()]
        self.tags = ', '.join(tag_names)
    
    def create_slug(self, title):
        """Создает slug с транслитерацией русского текста"""
        import re
        import uuid
        
        # Словарь для транслитерации
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        }
        
        # Транслитерируем
        result = ''
        for char in title:
            if char in translit_dict:
                result += translit_dict[char]
            else:
                result += char
        
        # Приводим к нижнему регистру и очищаем
        slug = result.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Если slug пустой, создаем случайный
        if not slug:
            slug = f'file-{uuid.uuid4().hex[:8]}'
        
        # Проверяем уникальность
        counter = 1
        original_slug = slug
        while ArchiveFile.objects.filter(slug=slug).exclude(id=self.id if self.id else None).exists():
            slug = f'{original_slug}-{counter}'
            counter += 1
        
        return slug
    
    @property
    def file_size(self):
        """Возвращает размер файла в читаемом формате"""
        if self.file:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return "0 B"
    
    @property
    def file_extension(self):
        """Возвращает расширение файла"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ""


class FileComment(models.Model):
    """Модель комментариев к файлам"""
    file = models.ForeignKey(ArchiveFile, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_comments')
    content = models.TextField('Содержание')
    likes_count = models.PositiveIntegerField('Количество лайков', default=0)
    is_approved = models.BooleanField('Одобрен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Комментарий к файлу'
        verbose_name_plural = 'Комментарии к файлам'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Комментарий от {self.author.username} к "{self.file.title}"'


class FileLike(models.Model):
    """Модель лайков для файлов"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_likes')
    file = models.ForeignKey(ArchiveFile, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лайк файла'
        verbose_name_plural = 'Лайки файлов'
        unique_together = [['user', 'file']]
    
    def __str__(self):
        return f'{self.user.username} лайкнул {self.file.title}'


class Download(models.Model):
    """Модель для отслеживания скачиваний"""
    file = models.ForeignKey(ArchiveFile, on_delete=models.CASCADE, related_name='downloads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='downloads')
    ip_address = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    downloaded_at = models.DateTimeField('Дата скачивания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Скачивание'
        verbose_name_plural = 'Скачивания'
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f'Скачивание {self.file.title} в {self.downloaded_at}'


class Playlist(models.Model):
    """Модель плейлистов для файлов"""
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    files = models.ManyToManyField(ArchiveFile, related_name='playlists', blank=True)
    is_public = models.BooleanField('Публичный', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('Archive:playlist_detail', kwargs={'pk': self.pk})
