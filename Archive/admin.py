from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import FileCategory, ArchiveFile, FileComment, FileLike, Download, Playlist


@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    """Админка для категорий файлов"""
    list_display = ('name', 'slug', 'color_display', 'files_count_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('files_count_display', 'created_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Внешний вид', {
            'fields': ('color', 'icon', 'image'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('files_count_display',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def files_count_display(self, obj):
        """Отображение количества файлов с ссылкой"""
        if obj:
            count = obj.files.filter(is_public=True).count()
            if count > 0:
                url = reverse('admin:Archive_archivefile_changelist') + f'?category__id__exact={obj.id}'
                return format_html('<a href="{}">{} файлов</a>', url, count)
            return '0 файлов'
        return '-'
    files_count_display.short_description = 'Количество файлов'
    
    def color_display(self, obj):
        """Отображение цвета категории"""
        if obj and obj.color:
            return format_html(
                '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
                obj.color, obj.color
            )
        return '-'
    color_display.short_description = 'Цвет'


@admin.register(ArchiveFile)
class ArchiveFileAdmin(admin.ModelAdmin):
    """Админка для файлов архива"""
    list_display = ('title', 'file_type', 'uploaded_by', 'category', 'file_size_display', 'downloads_count', 'views_count', 'is_public', 'uploaded_at')
    list_filter = ('file_type', 'is_public', 'is_featured', 'allow_comments', 'uploaded_at', 'category')
    search_fields = ('title', 'description', 'uploaded_by__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('file_size_display', 'downloads_count', 'views_count', 'likes_count', 'uploaded_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description', 'file', 'file_type')
        }),
        ('Классификация', {
            'fields': ('category', 'tag_objects', 'tags')
        }),
        ('Автор и настройки', {
            'fields': ('uploaded_by', 'is_public', 'is_featured', 'allow_comments')
        }),
        ('Статистика', {
            'fields': ('downloads_count', 'views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        """Отображение размера файла"""
        return obj.file_size
    file_size_display.short_description = 'Размер файла'


@admin.register(FileComment)
class FileCommentAdmin(admin.ModelAdmin):
    """Админка для комментариев к файлам"""
    list_display = ('file', 'author', 'content_preview', 'likes_count', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'file__file_type')
    search_fields = ('content', 'author__username', 'file__title')
    readonly_fields = ('likes_count', 'created_at', 'updated_at')
    
    def content_preview(self, obj):
        """Предварительный просмотр комментария"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Содержание'


@admin.register(FileLike)
class FileLikeAdmin(admin.ModelAdmin):
    """Админка для лайков файлов"""
    list_display = ('user', 'file', 'created_at')
    list_filter = ('created_at', 'file__file_type')
    search_fields = ('user__username', 'file__title')


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    """Админка для скачиваний"""
    list_display = ('file', 'user', 'ip_address', 'downloaded_at')
    list_filter = ('downloaded_at', 'file__file_type')
    search_fields = ('file__title', 'user__username', 'ip_address')
    readonly_fields = ('downloaded_at',)


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    """Админка для плейлистов"""
    list_display = ('name', 'created_by', 'files_count', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description', 'created_by__username')
    filter_horizontal = ('files',)
    readonly_fields = ('created_at', 'updated_at')
    
    def files_count(self, obj):
        """Количество файлов в плейлисте"""
        return obj.files.count()
    files_count.short_description = 'Количество файлов'
