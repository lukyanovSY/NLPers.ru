"""
Основные настройки Django Admin для проекта NLPers.ru
"""

from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

# Настройки заголовков и названий админ-панели
admin.site.site_header = "NLPers.ru - Панель администрирования"
admin.site.site_title = "NLPers.ru Admin"
admin.site.index_title = "Добро пожаловать в панель управления NLPers.ru"

# Дополнительные настройки
admin.site.site_url = "/"  # Ссылка "Просмотреть сайт"
admin.site.enable_nav_sidebar = True  # Включить боковую навигацию


class AdminMixin:
    """Базовый миксин для улучшения админ-интерфейса"""
    
    def get_readonly_fields(self, request, obj=None):
        """Автоматически добавляем поля created_at и updated_at в readonly"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if hasattr(self.model, 'created_at') and 'created_at' not in readonly_fields:
            readonly_fields.append('created_at')
        if hasattr(self.model, 'updated_at') and 'updated_at' not in readonly_fields:
            readonly_fields.append('updated_at')
        return readonly_fields
    
    def get_list_display(self, request):
        """Автоматически добавляем важные поля в list_display"""
        list_display = list(super().get_list_display(request) if hasattr(super(), 'get_list_display') else self.list_display or [])
        
        # Добавляем ID если его нет
        if 'id' not in list_display and len(list_display) < 5:
            list_display.insert(0, 'id')
            
        # Добавляем created_at если есть
        if hasattr(self.model, 'created_at') and 'created_at' not in list_display:
            list_display.append('created_at')
            
        return list_display
    
    def get_list_filter(self, request):
        """Автоматически добавляем фильтры по датам"""
        list_filter = list(super().get_list_filter(request) if hasattr(super(), 'get_list_filter') else self.list_filter or [])
        
        if hasattr(self.model, 'created_at') and 'created_at' not in list_filter:
            list_filter.append('created_at')
            
        if hasattr(self.model, 'is_active') and 'is_active' not in list_filter:
            list_filter.append('is_active')
            
        return list_filter


# Улучшенная конфигурация для User
class CustomUserAdmin(AdminMixin, BaseUserAdmin):
    """Расширенная админка для пользователей"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets
    
    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related()


# Улучшенная конфигурация для Groups
class CustomGroupAdmin(AdminMixin, BaseGroupAdmin):
    """Расширенная админка для групп"""
    
    list_display = ('name', 'permissions_count')
    search_fields = ('name',)
    
    def permissions_count(self, obj):
        """Показываем количество разрешений в группе"""
        count = obj.permissions.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    permissions_count.short_description = 'Количество разрешений'


# Перерегистрируем стандартные модели с улучшенными настройками
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)


# Функция для добавления кастомных действий
def make_published(modeladmin, request, queryset):
    """Массовое действие - опубликовать"""
    updated = queryset.update(status='published')
    modeladmin.message_user(request, f'{updated} записей было опубликовано.')
make_published.short_description = "Опубликовать выбранные записи"


def make_draft(modeladmin, request, queryset):
    """Массовое действие - перевести в черновики"""
    updated = queryset.update(status='draft')
    modeladmin.message_user(request, f'{updated} записей переведено в черновики.')
make_draft.short_description = "Перевести в черновики"


def activate_items(modeladmin, request, queryset):
    """Массовое действие - активировать"""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f'{updated} записей было активировано.')
activate_items.short_description = "Активировать выбранные записи"


def deactivate_items(modeladmin, request, queryset):
    """Массовое действие - деактивировать"""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f'{updated} записей было деактивировано.')
deactivate_items.short_description = "Деактивировать выбранные записи"


# Дополнительные утилиты для админки
class ImagePreviewMixin:
    """Миксин для предварительного просмотра изображений"""
    
    def image_preview(self, obj, field_name, width=100, height=100):
        """Генерирует превью изображения"""
        field = getattr(obj, field_name)
        if field:
            return format_html(
                '<img src="{}" style="max-width: {}px; max-height: {}px; border: 1px solid #ddd; border-radius: 4px;" />',
                field.url, width, height
            )
        return "Нет изображения"


class LinkMixin:
    """Миксин для создания ссылок на связанные объекты"""
    
    def create_link(self, obj, field_name, link_text=None):
        """Создает ссылку на связанный объект"""
        related_obj = getattr(obj, field_name)
        if related_obj:
            link_text = link_text or str(related_obj)
            url = reverse(f'admin:{related_obj._meta.app_label}_{related_obj._meta.model_name}_change', 
                         args=[related_obj.pk])
            return format_html('<a href="{}">{}</a>', url, link_text)
        return "-"


# Базовый класс для всех админок проекта
class BaseModelAdmin(AdminMixin, ImagePreviewMixin, LinkMixin, admin.ModelAdmin):
    """Базовый класс для всех админок с общими настройками"""
    
    save_on_top = True  # Кнопки сохранения вверху
    list_per_page = 25  # Количество записей на странице
    list_max_show_all = 100  # Максимум записей для "показать все"
    
    # Общие действия для всех моделей
    actions = [activate_items, deactivate_items]
    
    def get_actions(self, request):
        """Добавляем действия в зависимости от модели"""
        actions = super().get_actions(request)
        
        # Добавляем действия для моделей со статусом
        if hasattr(self.model, 'status'):
            actions['make_published'] = (make_published, 'make_published', make_published.short_description)
            actions['make_draft'] = (make_draft, 'make_draft', make_draft.short_description)
            
        # Убираем действия для моделей без is_active
        if not hasattr(self.model, 'is_active'):
            if 'activate_items' in actions:
                del actions['activate_items']
            if 'deactivate_items' in actions:
                del actions['deactivate_items']
                
        return actions
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)