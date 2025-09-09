from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Админ-панель для настроек сайта"""
    
    def has_add_permission(self, request):
        # Разрешаем создание только если настроек еще нет
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление настроек
        return False
    
    fieldsets = (
        ('Основные настройки', {
            'fields': ('site_name', 'site_description', 'contact_email')
        }),
        ('Внешний вид', {
            'fields': (
                'background_image', 
                'background_preview',
                'background_overlay_opacity', 
                'header_background_color',
                'logo',
                'logo_preview',
                'favicon'
            ),
            'description': 'Настройки внешнего вида сайта'
        }),
        ('Социальные сети', {
            'fields': ('social_links',),
            'classes': ('collapse',),
            'description': 'Ссылки на социальные сети в формате JSON. Пример: {"twitter": "https://twitter.com/example", "facebook": "https://facebook.com/example"}'
        }),
        ('Дополнительно', {
            'fields': ('analytics_code', 'maintenance_mode'),
            'classes': ('collapse',),
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'background_preview',
        'logo_preview'
    )
    
    list_display = (
        'site_name', 
        'maintenance_mode', 
        'has_background_image',
        'has_logo',
        'updated_at'
    )
    
    def background_preview(self, obj):
        """Превью фонового изображения"""
        if obj.background_image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 100px; border: 1px solid #ddd;" />',
                obj.background_image.url
            )
        return "Не загружено"
    background_preview.short_description = "Превью фона"
    
    def logo_preview(self, obj):
        """Превью логотипа"""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 50px; border: 1px solid #ddd;" />',
                obj.logo.url
            )
        return "Не загружено"
    logo_preview.short_description = "Превью логотипа"
    
    def has_background_image(self, obj):
        """Проверка наличия фонового изображения"""
        return bool(obj.background_image)
    has_background_image.boolean = True
    has_background_image.short_description = "Фон загружен"
    
    def has_logo(self, obj):
        """Проверка наличия логотипа"""
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = "Логотип загружен"
    
    def changelist_view(self, request, extra_context=None):
        """Переопределяем представление списка"""
        # Если настроек нет, создаем их
        if not SiteSettings.objects.exists():
            SiteSettings.get_settings()
        
        # Если есть настройки, перенаправляем на редактирование
        if SiteSettings.objects.exists():
            settings = SiteSettings.objects.first()
            return self.change_view(request, str(settings.pk), extra_context)
        
        return super().changelist_view(request, extra_context)
    
    class Media:
        css = {
            'all': ('admin/css/site_settings.css',)
        }
        js = ('admin/js/site_settings.js',)
