"""
Сигналы для автоматической инвалидации кэша
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ArchiveFile, FileCategory
from .cache_utils import invalidate_file_cache


@receiver(post_save, sender=ArchiveFile)
def invalidate_file_cache_on_save(sender, instance, **kwargs):
    """Инвалидирует кэш при сохранении файла"""
    invalidate_file_cache(
        file_id=instance.id,
        category_id=instance.category.id if instance.category else None,
        username=instance.uploaded_by.username
    )


@receiver(post_delete, sender=ArchiveFile)
def invalidate_file_cache_on_delete(sender, instance, **kwargs):
    """Инвалидирует кэш при удалении файла"""
    invalidate_file_cache(
        category_id=instance.category.id if instance.category else None,
        username=instance.uploaded_by.username
    )


@receiver(post_save, sender=FileCategory)
def invalidate_category_cache_on_save(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении категории файлов"""
    invalidate_file_cache(category_id=instance.id)
