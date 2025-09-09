"""
Утилиты для кэширования в приложении Archive
"""
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import hashlib


def get_cache_key(*args, **kwargs):
    """Генерирует ключ кэша на основе аргументов"""
    key_string = '_'.join(str(arg) for arg in args)
    if kwargs:
        key_string += '_' + '_'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_files_list(category_id=None, file_type=None, page=1):
    """Кэширует список файлов с фильтрацией"""
    cache_key = get_cache_key(
        'files_list',
        category_id or 'all',
        file_type or 'all',
        page
    )
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import ArchiveFile, FileCategory
    
    # Базовый запрос
    files = ArchiveFile.objects.filter(is_public=True).select_related(
        'category', 'uploaded_by'
    ).prefetch_related('tag_objects')
    
    # Применяем фильтры
    if category_id:
        files = files.filter(category_id=category_id)
    if file_type:
        files = files.filter(file_type=file_type)
    
    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(files, 12)  # 12 файлов на страницу
    page_obj = paginator.get_page(page)
    
    result = {
        'files': list(page_obj.object_list.values(
            'id', 'title', 'slug', 'description', 'thumbnail',
            'file_type', 'downloads_count', 'views_count', 'likes_count',
            'uploaded_at', 'is_featured',
            'category__name', 'category__slug', 'category__color',
            'uploaded_by__username'
        )),
        'page_obj': page_obj,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'num_pages': page_obj.paginator.num_pages,
    }
    
    # Кэшируем на 15 минут
    cache.set(cache_key, result, 900)
    return result


def cache_featured_files(limit=8):
    """Кэширует рекомендуемые файлы"""
    cache_key = get_cache_key('featured_files', limit)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import ArchiveFile
    
    featured_files = ArchiveFile.objects.filter(
        is_public=True,
        is_featured=True
    ).select_related('category', 'uploaded_by').order_by('-uploaded_at')[:limit]
    
    result = list(featured_files.values(
        'id', 'title', 'slug', 'description', 'thumbnail',
        'file_type', 'downloads_count', 'views_count', 'likes_count',
        'uploaded_at',
        'category__name', 'category__slug', 'category__color',
        'uploaded_by__username'
    ))
    
    # Кэшируем на 1 час
    cache.set(cache_key, result, 3600)
    return result


def cache_recent_files(limit=8):
    """Кэширует последние файлы"""
    cache_key = get_cache_key('recent_files', limit)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import ArchiveFile
    
    recent_files = ArchiveFile.objects.filter(
        is_public=True
    ).select_related('category', 'uploaded_by').order_by('-uploaded_at')[:limit]
    
    result = list(recent_files.values(
        'id', 'title', 'slug', 'description', 'thumbnail',
        'file_type', 'downloads_count', 'views_count', 'likes_count',
        'uploaded_at',
        'category__name', 'category__slug', 'category__color',
        'uploaded_by__username'
    ))
    
    # Кэшируем на 30 минут
    cache.set(cache_key, result, 1800)
    return result


def cache_popular_files(limit=8):
    """Кэширует популярные файлы"""
    cache_key = get_cache_key('popular_files', limit)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import ArchiveFile
    
    # Файлы с наибольшим количеством скачиваний за последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    popular_files = ArchiveFile.objects.filter(
        is_public=True,
        uploaded_at__gte=thirty_days_ago
    ).select_related('category', 'uploaded_by').order_by('-downloads_count')[:limit]
    
    result = list(popular_files.values(
        'id', 'title', 'slug', 'description', 'thumbnail',
        'file_type', 'downloads_count', 'views_count', 'likes_count',
        'uploaded_at',
        'category__name', 'category__slug', 'category__color',
        'uploaded_by__username'
    ))
    
    # Кэшируем на 1 час
    cache.set(cache_key, result, 3600)
    return result


def cache_file_categories():
    """Кэширует категории файлов с количеством"""
    cache_key = get_cache_key('file_categories')
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import FileCategory
    
    categories = FileCategory.objects.filter(
        is_active=True
    ).annotate(
        files_count=Count('files', filter=Q(files__is_public=True))
    ).order_by('name')
    
    result = list(categories.values(
        'id', 'name', 'slug', 'description', 'color', 'icon', 'image', 'files_count'
    ))
    
    # Кэшируем на 2 часа
    cache.set(cache_key, result, 7200)
    return result


def cache_file_detail(file_id):
    """Кэширует детали файла"""
    cache_key = get_cache_key('file_detail', file_id)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import ArchiveFile
    
    try:
        file_obj = ArchiveFile.objects.select_related(
            'category', 'uploaded_by'
        ).prefetch_related(
            'tag_objects', 'comments__author'
        ).get(id=file_id, is_public=True)
        
        result = {
            'id': file_obj.id,
            'title': file_obj.title,
            'slug': file_obj.slug,
            'description': file_obj.description,
            'file': file_obj.file.url if file_obj.file else None,
            'thumbnail': file_obj.thumbnail.url if file_obj.thumbnail else None,
            'file_type': file_obj.file_type,
            'file_size': file_obj.file_size,
            'file_extension': file_obj.file_extension,
            'downloads_count': file_obj.downloads_count,
            'views_count': file_obj.views_count,
            'likes_count': file_obj.likes_count,
            'uploaded_at': file_obj.uploaded_at,
            'is_featured': file_obj.is_featured,
            'category': {
                'id': file_obj.category.id if file_obj.category else None,
                'name': file_obj.category.name if file_obj.category else None,
                'slug': file_obj.category.slug if file_obj.category else None,
                'color': file_obj.category.color if file_obj.category else None,
            },
            'uploaded_by': {
                'username': file_obj.uploaded_by.username,
                'first_name': file_obj.uploaded_by.first_name,
                'last_name': file_obj.uploaded_by.last_name,
            },
            'tags': list(file_obj.tag_objects.filter(is_active=True).values(
                'name', 'slug', 'color'
            )),
        }
        
        # Кэшируем на 1 час
        cache.set(cache_key, result, 3600)
        return result
        
    except ArchiveFile.DoesNotExist:
        return None


def cache_user_files(username, page=1):
    """Кэширует файлы пользователя"""
    cache_key = get_cache_key('user_files', username, page)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import ArchiveFile
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(username=username)
        files = ArchiveFile.objects.filter(
            uploaded_by=user,
            is_public=True
        ).select_related('category').order_by('-uploaded_at')
        
        # Пагинация
        from django.core.paginator import Paginator
        paginator = Paginator(files, 12)
        page_obj = paginator.get_page(page)
        
        result = {
            'files': list(page_obj.object_list.values(
                'id', 'title', 'slug', 'description', 'thumbnail',
                'file_type', 'downloads_count', 'views_count', 'likes_count',
                'uploaded_at', 'is_featured',
                'category__name', 'category__slug', 'category__color'
            )),
            'page_obj': page_obj,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'num_pages': page_obj.paginator.num_pages,
        }
        
        # Кэшируем на 30 минут
        cache.set(cache_key, result, 1800)
        return result
        
    except User.DoesNotExist:
        return None


def invalidate_file_cache(file_id=None, category_id=None, username=None):
    """Инвалидирует кэш файлов при изменении"""
    # Очищаем кэш списков файлов
    cache.delete_many([
        get_cache_key('files_list', 'all', 'all', 1),
        get_cache_key('featured_files', 8),
        get_cache_key('recent_files', 8),
        get_cache_key('popular_files', 8),
    ])
    
    # Очищаем кэш категорий
    cache.delete(get_cache_key('file_categories'))
    
    # Очищаем кэш конкретного файла
    if file_id:
        cache.delete(get_cache_key('file_detail', file_id))
    
    # Очищаем кэш по категории
    if category_id:
        for page in range(1, 10):  # Очищаем первые 10 страниц
            cache.delete(get_cache_key('files_list', category_id, 'all', page))
    
    # Очищаем кэш пользователя
    if username:
        for page in range(1, 10):  # Очищаем первые 10 страниц
            cache.delete(get_cache_key('user_files', username, page))


def cache_file_statistics():
    """Кэширует статистику файлов"""
    cache_key = get_cache_key('file_statistics')
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import ArchiveFile, FileCategory
    
    stats = {
        'total_files': ArchiveFile.objects.filter(is_public=True).count(),
        'total_downloads': ArchiveFile.objects.filter(is_public=True).aggregate(
            total=Count('downloads_count')
        )['total'] or 0,
        'files_by_type': list(ArchiveFile.objects.filter(is_public=True).values(
            'file_type'
        ).annotate(count=Count('id'))),
        'categories_count': FileCategory.objects.filter(is_active=True).count(),
    }
    
    # Кэшируем на 1 час
    cache.set(cache_key, stats, 3600)
    return stats
