from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db.models import Count
from NLPers.admin import BaseModelAdmin, make_published, make_draft

# Безопасный импорт моделей
try:
    from .models import Category, Post, Comment, Like, Follow, Newsletter, UserProfile, AuthorRequest, Tag
except ImportError:
    Category = Post = Comment = Like = Follow = Newsletter = UserProfile = AuthorRequest = Tag = None


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    """Админка для категорий постов"""
    list_display = ('name', 'slug', 'image_thumbnail', 'posts_count_display', 'color_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('posts_count_display', 'add_article_button', 'image_preview', 'created_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Внешний вид', {
            'fields': ('color', 'icon', 'image', 'image_preview'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('posts_count_display', 'add_article_button'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def posts_count_display(self, obj):
        """Отображение количества постов с ссылкой"""
        if obj:
            count = obj.posts.filter(status='published').count()
            if count > 0:
                url = reverse('admin:Blog_post_changelist') + f'?category__id__exact={obj.id}'
                return format_html('<a href="{}">{} постов</a>', url, count)
            return '0 постов'
        return '-'
    posts_count_display.short_description = 'Количество постов'
    
    def color_display(self, obj):
        """Отображение цвета категории"""
        if obj and obj.color:
            return format_html(
                '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
                obj.color, obj.color
            )
        return '-'
    color_display.short_description = 'Цвет'
    
    def image_thumbnail(self, obj):
        """Миниатюра изображения для списка"""
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return '—'
    image_thumbnail.short_description = 'Картинка'
    
    def image_preview(self, obj):
        """Превью изображения для формы"""
        if obj and obj.image:
            return format_html(
                '<div style="margin-top: 10px;"><img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.15);" /></div>',
                obj.image.url
            )
        return "Изображение не загружено"
    
    def add_article_button(self, obj):
        """Кнопка для добавления статьи в категорию"""
        if obj and obj.pk:
            url = reverse('admin:Blog_post_add') + f'?category={obj.pk}'
            return format_html(
                '<a href="{}" class="add-article-button button">➕ Добавить статью</a>',
                url
            )
        return format_html(
            '<span style="color: #6c757d; font-style: italic;">Сначала сохраните категорию</span>'
        )
    add_article_button.short_description = 'Действия'
    image_preview.short_description = 'Превью изображения'


@admin.register(Tag)
class TagAdmin(BaseModelAdmin):
    """Админка для тегов"""
    list_display = ('name', 'slug', 'color_display', 'posts_count_display', 'archive_files_count_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('posts_count_display', 'archive_files_count_display', 'created_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Внешний вид', {
            'fields': ('color', 'icon'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('posts_count_display', 'archive_files_count_display'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def posts_count_display(self, obj):
        """Отображение количества постов с ссылкой"""
        if obj:
            count = obj.posts.filter(status='published').count()
            if count > 0:
                url = reverse('admin:Blog_post_changelist') + f'?tag_objects__id__exact={obj.id}'
                return format_html('<a href="{}">{} постов</a>', url, count)
            return '0 постов'
        return '-'
    posts_count_display.short_description = 'Количество постов'
    
    def archive_files_count_display(self, obj):
        """Отображение количества файлов архива с ссылкой"""
        if obj:
            try:
                from Archive.models import ArchiveFile
                count = ArchiveFile.objects.filter(tag_objects=obj, is_public=True).count()
                if count > 0:
                    url = reverse('admin:Archive_archivefile_changelist') + f'?tag_objects__id__exact={obj.id}'
                    return format_html('<a href="{}">{} файлов</a>', url, count)
                return '0 файлов'
            except ImportError:
                return 'Архив недоступен'
        return '-'
    archive_files_count_display.short_description = 'Количество файлов'
    
    def color_display(self, obj):
        """Отображение цвета тега"""
        if obj and obj.color:
            return format_html(
                '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
                obj.color, obj.color
            )
        return '-'
    color_display.short_description = 'Цвет'


class CommentInline(admin.TabularInline):
    """Инлайн для комментариев в посте"""
    model = Comment
    extra = 0
    fields = ('author', 'content', 'is_approved', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True


@admin.register(Post)
class PostAdmin(BaseModelAdmin):
    """Админка для постов"""
    list_display = ('featured_image_thumbnail', 'title', 'author', 'category', 'status', 'is_featured', 'views_count', 'likes_count', 'comments_count', 'published_at')
    list_filter = ('status', 'is_featured', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'tags', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    actions = [make_published, make_draft]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Содержание', {
            'fields': ('content', 'excerpt', 'tags', 'tag_objects')
        }),
        ('Медиа', {
            'fields': ('featured_image', 'featured_image_preview'),
            'classes': ('collapse',)
        }),
        ('Настройки', {
            'fields': ('is_featured', 'allow_comments'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('views_count', 'likes_count', 'comments_count', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('featured_image_preview', 'views_count', 'likes_count', 'comments_count', 'reading_time', 'created_at', 'updated_at')
    inlines = [CommentInline]
    
    def featured_image_preview(self, obj):
        """Превью главного изображения"""
        return self.image_preview(obj, 'featured_image', 200, 150)
    featured_image_preview.short_description = 'Превью изображения'
    
    def featured_image_thumbnail(self, obj):
        """Миниатюра изображения для списка постов"""
        if obj and obj.featured_image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 45px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" />',
                obj.featured_image.url
            )
        return format_html('<span style="color: #999; font-size: 12px;">Нет изображения</span>')
    featured_image_thumbnail.short_description = '🖼️ Превью'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('author', 'category').prefetch_related('comments')
    
    def get_changeform_initial_data(self, request):
        """Предзаполнение формы значениями из GET-параметров"""
        initial = super().get_changeform_initial_data(request)
        
        # Предзаполняем категорию, если она передана в GET-параметрах
        if 'category' in request.GET:
            try:
                category_id = int(request.GET['category'])
                if Category and Category.objects.filter(id=category_id).exists():
                    initial['category'] = category_id
            except (ValueError, TypeError):
                pass
                
        # Устанавливаем автора по умолчанию
        if not initial.get('author'):
            initial['author'] = request.user.id
            
        return initial


@admin.register(AuthorRequest)
class AuthorRequestAdmin(BaseModelAdmin):
    """Админка для заявок на авторство"""
    list_display = ('user', 'status', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('user__username', 'user__email', 'motivation')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Информация о пользователе', {
            'fields': ('user',)
        }),
        ('Заявка', {
            'fields': ('motivation', 'experience', 'sample_topics')
        }),
        ('Рассмотрение', {
            'fields': ('status', 'admin_comment', 'reviewed_by', 'reviewed_at'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем рассматривающего администратора"""
        if change and 'status' in form.changed_data:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(BaseModelAdmin):
    """Админка для комментариев"""
    list_display = ('author', 'post_link', 'content_preview', 'is_approved', 'likes_count', 'created_at')
    list_filter = ('is_approved', 'created_at', 'post__category')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('created_at', 'updated_at', 'likes_count')
    actions = ['approve_comments', 'disapprove_comments']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('author', 'post', 'parent', 'content')
        }),
        ('Модерация', {
            'fields': ('is_approved',)
        }),
        ('Статистика', {
            'fields': ('likes_count',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def post_link(self, obj):
        """Ссылка на пост"""
        return self.create_link(obj, 'post')
    post_link.short_description = 'Пост'
    
    def content_preview(self, obj):
        """Краткий просмотр содержания"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Содержание'
    
    def approve_comments(self, request, queryset):
        """Одобрить комментарии"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} комментариев одобрено.')
    approve_comments.short_description = "Одобрить выбранные комментарии"
    
    def disapprove_comments(self, request, queryset):
        """Отклонить комментарии"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} комментариев отклонено.')
    disapprove_comments.short_description = "Отклонить выбранные комментарии"


@admin.register(UserProfile)
class UserProfileAdmin(BaseModelAdmin):
    """Админка для профилей пользователей"""
    list_display = ('user', 'is_verified', 'followers_count', 'following_count', 'posts_count', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    readonly_fields = ('avatar_preview', 'followers_count', 'following_count', 'posts_count', 'created_at')
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'is_verified')
        }),
        ('Профиль', {
            'fields': ('bio', 'location', 'avatar', 'avatar_preview')
        }),
        ('Ссылки', {
            'fields': ('website', 'github_url', 'linkedin_url'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('followers_count', 'following_count', 'posts_count'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def avatar_preview(self, obj):
        """Превью аватара"""
        return self.image_preview(obj, 'avatar', 100, 100)
    avatar_preview.short_description = 'Превью аватара'


@admin.register(Like)
class LikeAdmin(BaseModelAdmin):
    """Админка для лайков"""
    list_display = ('user', 'content_type', 'target_object', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    
    def target_object(self, obj):
        """Отображение целевого объекта"""
        if obj.content_type == 'post' and obj.post:
            return f"Пост: {obj.post.title}"
        elif obj.content_type == 'comment' and obj.comment:
            return f"Комментарий: {obj.comment.content[:50]}..."
        return "-"
    target_object.short_description = 'Объект'


@admin.register(Follow)
class FollowAdmin(BaseModelAdmin):
    """Админка для подписок"""
    list_display = ('follower', 'follow_type', 'target_object', 'created_at')
    list_filter = ('follow_type', 'created_at')
    search_fields = ('follower__username', 'following_user__username')
    readonly_fields = ('created_at',)
    
    def target_object(self, obj):
        """Отображение цели подписки"""
        if obj.follow_type == 'user' and obj.following_user:
            return f"Пользователь: {obj.following_user.username}"
        elif obj.follow_type == 'category' and obj.following_category:
            return f"Категория: {obj.following_category.name}"
        return "-"
    target_object.short_description = 'Цель подписки'


@admin.register(Newsletter)
class NewsletterAdmin(BaseModelAdmin):
    """Админка для подписок на рассылку"""
    list_display = ('email', 'is_active', 'confirmed_at', 'created_at')
    list_filter = ('is_active', 'confirmed_at', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        """Активировать подписки"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} подписок активировано.')
    activate_subscriptions.short_description = "Активировать выбранные подписки"
    
    def deactivate_subscriptions(self, request, queryset):
        """Деактивировать подписки"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} подписок деактивировано.')
    deactivate_subscriptions.short_description = "Деактивировать выбранные подписки"


# Настройка заголовка для раздела Blog в админке
if Category:
    admin.site._registry[Category].verbose_name_plural = "🗂️ Категории постов"
if Post:
    admin.site._registry[Post].verbose_name_plural = "📝 Посты блога"
if Comment:
    admin.site._registry[Comment].verbose_name_plural = "💬 Комментарии"
