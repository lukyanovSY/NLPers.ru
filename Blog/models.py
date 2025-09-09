from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
import os


class Category(models.Model):
    """Модель категорий для постов блога"""
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)
    color = models.CharField('Цвет', max_length=7, default='#007bff', help_text='HEX цвет для отображения')
    icon = models.CharField('Иконка', max_length=50, blank=True, help_text='CSS класс Font Awesome')
    image = models.ImageField('Картинка', upload_to='categories/', blank=True, null=True, help_text='Изображение для категории (рекомендуется 400x300px)')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.create_slug(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('Blog:category_detail', kwargs={'slug': self.slug})
    
    @property
    def posts_count(self):
        return self.posts.filter(status='published').count()
    
    def create_slug(self, name):
        """Создает slug с транслитерацией русского текста"""
        import re
        import uuid
        
        # Расширенный словарь для транслитерации (поддержка заглавных и строчных)
        translit_dict = {
            # Строчные буквы
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            # Заглавные буквы
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
            'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA',
        }
        
        # Транслитерируем каждый символ
        result = ''
        for char in name:
            if char in translit_dict:
                result += translit_dict[char]
            else:
                result += char
        
        # Очищаем и форматируем slug
        slug = result.lower()  # Приводим к нижнему регистру
        slug = re.sub(r'[^\w\s-]', '', slug)  # Убираем специальные символы
        slug = re.sub(r'[-\s]+', '-', slug)  # Заменяем пробелы и множественные дефисы на один дефис
        slug = slug.strip('-')  # Убираем дефисы в начале и конце
        
        # Если slug пустой, создаем случайный
        if not slug:
            slug = f'category-{uuid.uuid4().hex[:8]}'
        
        # Проверяем уникальность
        from Blog.models import Category
        counter = 1
        original_slug = slug
        while Category.objects.filter(slug=slug).exclude(id=self.id if self.id else None).exists():
            slug = f'{original_slug}-{counter}'
            counter += 1
        
        return slug


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    bio = models.TextField('Биография', max_length=500, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    location = models.CharField('Местоположение', max_length=100, blank=True)
    website = models.URLField('Веб-сайт', blank=True)
    github_url = models.URLField('GitHub', blank=True)
    linkedin_url = models.URLField('LinkedIn', blank=True)
    is_verified = models.BooleanField('Верифицирован', default=False)
    followers_count = models.PositiveIntegerField('Количество подписчиков', default=0)
    following_count = models.PositiveIntegerField('Количество подписок', default=0)
    posts_count = models.PositiveIntegerField('Количество постов', default=0)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f'Профиль {self.user.username}'
    
    def get_absolute_url(self):
        return reverse('Blog:user_profile', kwargs={'username': self.user.username})


class Tag(models.Model):
    """Модель тегов для постов и файлов"""
    name = models.CharField('Название', max_length=50, unique=True)
    slug = models.SlugField('URL', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)
    color = models.CharField('Цвет', max_length=7, default='#6c757d', help_text='HEX цвет для отображения')
    icon = models.CharField('Иконка', max_length=50, blank=True, help_text='CSS класс Font Awesome')
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.create_slug(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('Blog:tag_detail', kwargs={'slug': self.slug})
    
    @property
    def posts_count(self):
        return self.posts.filter(status='published').count()
    
    @property
    def archive_files_count(self):
        try:
            from Archive.models import ArchiveFile
            return ArchiveFile.objects.filter(tag_objects=self, is_public=True).count()
        except ImportError:
            return 0
    
    @property
    def total_content_count(self):
        """Общее количество контента (посты + файлы)"""
        return self.posts_count + self.archive_files_count
    
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
            slug = f'tag-{uuid.uuid4().hex[:8]}'
        
        # Проверяем уникальность
        counter = 1
        original_slug = slug
        while Tag.objects.filter(slug=slug).exclude(id=self.id if self.id else None).exists():
            slug = f'{original_slug}-{counter}'
            counter += 1
        
        return slug


class Post(models.Model):
    """Модель постов блога"""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('archived', 'Архивировано'),
    ]
    
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name='Категория')
    content = CKEditor5Field('Содержание', config_name='extends')
    excerpt = models.TextField('Краткое описание', max_length=300, blank=True)
    featured_image = models.ImageField('Главное изображение', upload_to='posts/', blank=True, null=True)
    tags = models.CharField('Теги', max_length=200, blank=True, help_text='Разделяйте теги запятыми')
    tag_objects = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name='Теги')
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField('Рекомендуемый пост', default=False)
    allow_comments = models.BooleanField('Разрешить комментарии', default=True)
    views_count = models.PositiveIntegerField('Количество просмотров', default=0)
    likes_count = models.PositiveIntegerField('Количество лайков', default=0)
    comments_count = models.PositiveIntegerField('Количество комментариев', default=0)
    reading_time = models.PositiveIntegerField('Время чтения (мин)', default=1)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    published_at = models.DateTimeField('Дата публикации', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['author', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.create_slug(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        if not self.excerpt and self.content:
            # Удаляем HTML теги для excerpt
            import re
            clean_content = re.sub('<.*?>', '', self.content)
            self.excerpt = clean_content[:300] + '...' if len(clean_content) > 300 else clean_content
        
        # Синхронизируем теги
        super().save(*args, **kwargs)
        if self.tags:
            self.sync_tags_from_string()
    
    def get_absolute_url(self):
        return reverse('Blog:post_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        """Возвращает список тегов как строки"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_tag_objects(self):
        """Возвращает объекты тегов"""
        return self.tag_objects.filter(is_active=True)
    
    def sync_tags_from_string(self):
        """Синхронизирует теги из строки с объектами Tag"""
        if not self.tags:
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
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
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
            slug = f'post-{uuid.uuid4().hex[:8]}'
        
        # Проверяем уникальность
        from Blog.models import Post
        counter = 1
        original_slug = slug
        while Post.objects.filter(slug=slug).exclude(id=self.id if self.id else None).exists():
            slug = f'{original_slug}-{counter}'
            counter += 1
        
        return slug


class Comment(models.Model):
    """Модель комментариев к постам"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField('Содержание')
    likes_count = models.PositiveIntegerField('Количество лайков', default=0)
    is_approved = models.BooleanField('Одобрен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f'Комментарий от {self.author.username} к "{self.post.title}"'
    
    def get_replies(self):
        return self.replies.filter(is_approved=True).order_by('created_at')


class Like(models.Model):
    """Модель лайков для постов и комментариев"""
    CONTENT_TYPE_CHOICES = [
        ('post', 'Пост'),
        ('comment', 'Комментарий'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    content_type = models.CharField('Тип контента', max_length=10, choices=CONTENT_TYPE_CHOICES)
    object_id = models.PositiveIntegerField('ID объекта')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='post_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='comment_likes')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = [['user', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        target = self.post if self.content_type == 'post' else self.comment
        return f'{self.user.username} лайкнул {self.content_type}: {target}'


class Follow(models.Model):
    """Модель подписок пользователей"""
    FOLLOW_TYPE_CHOICES = [
        ('user', 'Пользователь'),
        ('category', 'Категория'),
    ]
    
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follow_type = models.CharField('Тип подписки', max_length=10, choices=FOLLOW_TYPE_CHOICES)
    following_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='followers')
    following_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='followers')
    created_at = models.DateTimeField('Дата подписки', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = [
            ['follower', 'following_user'],
            ['follower', 'following_category']
        ]
        indexes = [
            models.Index(fields=['follow_type', 'created_at']),
            models.Index(fields=['follower', 'follow_type']),
        ]
    
    def __str__(self):
        if self.follow_type == 'user':
            return f'{self.follower.username} подписан на {self.following_user.username}'
        else:
            return f'{self.follower.username} подписан на категорию {self.following_category.name}'





class Newsletter(models.Model):
    """Модель подписчиков рассылки"""
    email = models.EmailField('Email', unique=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата подписки', auto_now_add=True)
    confirmed_at = models.DateTimeField('Дата подтверждения', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Подписка на рассылку'
        verbose_name_plural = 'Подписки на рассылку'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Подписка: {self.email}'


# Сигналы для автоматического создания профиля пользователя
from django.db.models.signals import post_save
from django.dispatch import receiver

class AuthorRequest(models.Model):
    """Модель заявки на статус автора"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_request', verbose_name='Пользователь')
    motivation = models.TextField('Мотивация', max_length=1000, help_text='Расскажите, почему хотите стать автором')
    experience = models.TextField('Опыт', max_length=1000, blank=True, help_text='Опишите свой опыт в области, о которой планируете писать')
    sample_topics = models.TextField('Примеры тем', max_length=1000, blank=True, help_text='Какие темы планируете освещать?')
    
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField('Комментарий администратора', blank=True)
    
    created_at = models.DateTimeField('Дата подачи заявки', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests', verbose_name='Рассмотрена')
    reviewed_at = models.DateTimeField('Дата рассмотрения', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Заявка на авторство'
        verbose_name_plural = 'Заявки на авторство'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Заявка от {self.user.username} - {self.get_status_display()}'
    
    def save(self, *args, **kwargs):
        # Если заявка одобрена, добавляем пользователя в группу авторов
        if self.status == 'approved' and self.pk:
            old_instance = AuthorRequest.objects.get(pk=self.pk)
            if old_instance.status != 'approved':
                from django.contrib.auth.models import Group
                author_group, created = Group.objects.get_or_create(name='Authors')
                self.user.groups.add(author_group)
                self.reviewed_at = timezone.now()
        
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()