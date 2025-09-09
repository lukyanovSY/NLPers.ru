"""
Сигналы для автоматической инвалидации кэша
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Post, Category, Tag, UserProfile
from .cache_utils import invalidate_post_cache, invalidate_user_cache


@receiver(post_save, sender=Post)
def invalidate_post_cache_on_save(sender, instance, **kwargs):
    """Инвалидирует кэш при сохранении поста"""
    invalidate_post_cache(
        post_slug=instance.slug,
        category_slug=instance.category.slug if instance.category else None
    )
    
    # Инвалидируем кэш тегов
    for tag in instance.tag_objects.all():
        invalidate_post_cache(tag_slug=tag.slug)


@receiver(post_delete, sender=Post)
def invalidate_post_cache_on_delete(sender, instance, **kwargs):
    """Инвалидирует кэш при удалении поста"""
    invalidate_post_cache(
        category_slug=instance.category.slug if instance.category else None
    )
    
    # Инвалидируем кэш тегов
    for tag in instance.tag_objects.all():
        invalidate_post_cache(tag_slug=tag.slug)


@receiver(post_save, sender=Category)
def invalidate_category_cache_on_save(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении категории"""
    invalidate_post_cache(category_slug=instance.slug)


@receiver(post_save, sender=Tag)
def invalidate_tag_cache_on_save(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении тега"""
    invalidate_post_cache(tag_slug=instance.slug)


@receiver(post_save, sender=UserProfile)
def invalidate_user_cache_on_save(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении профиля пользователя"""
    invalidate_user_cache(instance.user.username)
