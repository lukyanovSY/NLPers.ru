"""
Утилиты для кэширования в приложении Blog
"""
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
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


def cache_posts_list(category_slug=None, tag_slug=None, author_username=None, page=1):
    """Кэширует список постов с фильтрацией"""
    cache_key = get_cache_key(
        'posts_list',
        category_slug or 'all',
        tag_slug or 'all', 
        author_username or 'all',
        page
    )
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import Post, Category, Tag
    
    # Базовый запрос
    posts = Post.objects.filter(status='published').select_related(
        'author', 'category'
    ).prefetch_related('tag_objects')
    
    # Применяем фильтры
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if tag_slug:
        posts = posts.filter(tag_objects__slug=tag_slug)
    if author_username:
        posts = posts.filter(author__username=author_username)
    
    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page)
    
    result = {
        'posts': list(page_obj.object_list.values(
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'views_count', 'likes_count', 'comments_count',
            'created_at', 'published_at',
            'author__username', 'author__first_name', 'author__last_name',
            'category__name', 'category__slug', 'category__color'
        )),
        'page_obj': page_obj,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'num_pages': page_obj.paginator.num_pages,
    }
    
    # Кэшируем на 10 минут
    cache.set(cache_key, result, 600)
    return result


def cache_popular_posts(limit=5):
    """Кэширует популярные посты"""
    cache_key = get_cache_key('popular_posts', limit)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import Post
    
    # Посты с наибольшим количеством просмотров за последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    popular_posts = Post.objects.filter(
        status='published',
        published_at__gte=thirty_days_ago
    ).select_related('author', 'category').order_by('-views_count')[:limit]
    
    result = list(popular_posts.values(
        'id', 'title', 'slug', 'excerpt', 'featured_image',
        'views_count', 'likes_count', 'created_at',
        'author__username', 'category__name', 'category__color'
    ))
    
    # Кэшируем на 1 час
    cache.set(cache_key, result, 3600)
    return result


def cache_recent_posts(limit=5):
    """Кэширует последние посты"""
    cache_key = get_cache_key('recent_posts', limit)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import Post
    
    recent_posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-published_at')[:limit]
    
    result = list(recent_posts.values(
        'id', 'title', 'slug', 'excerpt', 'featured_image',
        'views_count', 'likes_count', 'created_at',
        'author__username', 'category__name', 'category__color'
    ))
    
    # Кэшируем на 30 минут
    cache.set(cache_key, result, 1800)
    return result


def cache_categories_with_counts():
    """Кэширует категории с количеством постов"""
    cache_key = get_cache_key('categories_with_counts')
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import Category
    
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        posts_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('name')
    
    result = list(categories.values(
        'id', 'name', 'slug', 'description', 'color', 'icon', 'image', 'posts_count'
    ))
    
    # Кэшируем на 2 часа
    cache.set(cache_key, result, 7200)
    return result


def cache_tags_with_counts():
    """Кэширует теги с количеством постов"""
    cache_key = get_cache_key('tags_with_counts')
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import Tag
    
    tags = Tag.objects.filter(
        is_active=True
    ).annotate(
        posts_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('name')
    
    result = list(tags.values(
        'id', 'name', 'slug', 'description', 'color', 'icon', 'posts_count'
    ))
    
    # Кэшируем на 2 часа
    cache.set(cache_key, result, 7200)
    return result


def cache_post_detail(post_slug):
    """Кэширует детали поста"""
    cache_key = get_cache_key('post_detail', post_slug)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import Post
    
    try:
        post = Post.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tag_objects', 'comments__author'
        ).get(slug=post_slug, status='published')
        
        result = {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'content': post.content,
            'excerpt': post.excerpt,
            'featured_image': post.featured_image.url if post.featured_image else None,
            'views_count': post.views_count,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'reading_time': post.reading_time,
            'created_at': post.created_at,
            'published_at': post.published_at,
            'author': {
                'username': post.author.username,
                'first_name': post.author.first_name,
                'last_name': post.author.last_name,
            },
            'category': {
                'name': post.category.name if post.category else None,
                'slug': post.category.slug if post.category else None,
                'color': post.category.color if post.category else None,
            },
            'tags': list(post.tag_objects.filter(is_active=True).values(
                'name', 'slug', 'color'
            )),
        }
        
        # Кэшируем на 1 час
        cache.set(cache_key, result, 3600)
        return result
        
    except Post.DoesNotExist:
        return None


def invalidate_post_cache(post_slug=None, category_slug=None, tag_slug=None):
    """Инвалидирует кэш постов при изменении"""
    # Очищаем кэш списков постов
    cache.delete_many([
        get_cache_key('posts_list', 'all', 'all', 'all', 1),
        get_cache_key('popular_posts', 5),
        get_cache_key('recent_posts', 5),
    ])
    
    # Очищаем кэш категорий и тегов
    cache.delete_many([
        get_cache_key('categories_with_counts'),
        get_cache_key('tags_with_counts'),
    ])
    
    # Очищаем кэш конкретного поста
    if post_slug:
        cache.delete(get_cache_key('post_detail', post_slug))
    
    # Очищаем кэш по категории
    if category_slug:
        for page in range(1, 10):  # Очищаем первые 10 страниц
            cache.delete(get_cache_key('posts_list', category_slug, 'all', 'all', page))
    
    # Очищаем кэш по тегу
    if tag_slug:
        for page in range(1, 10):  # Очищаем первые 10 страниц
            cache.delete(get_cache_key('posts_list', 'all', tag_slug, 'all', page))


def cache_user_profile(username):
    """Кэширует профиль пользователя"""
    cache_key = get_cache_key('user_profile', username)
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    from .models import UserProfile
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.select_related('userprofile').get(username=username)
        profile = user.userprofile
        
        result = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'date_joined': user.date_joined,
            'bio': profile.bio,
            'avatar': profile.avatar.url if profile.avatar else None,
            'location': profile.location,
            'website': profile.website,
            'github_url': profile.github_url,
            'linkedin_url': profile.linkedin_url,
            'is_verified': profile.is_verified,
            'followers_count': profile.followers_count,
            'following_count': profile.following_count,
            'posts_count': profile.posts_count,
        }
        
        # Кэшируем на 30 минут
        cache.set(cache_key, result, 1800)
        return result
        
    except User.DoesNotExist:
        return None


def invalidate_user_cache(username):
    """Инвалидирует кэш пользователя"""
    cache.delete(get_cache_key('user_profile', username))
