"""
Утилиты для блога NLPers.ru
"""

import re
import uuid
from django.utils.text import slugify


def transliterate_russian(text):
    """
    Транслитерирует русский текст в латиницу
    Поддерживает все русские буквы в верхнем и нижнем регистре
    """
    
    # Расширенный словарь для транслитерации
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
    for char in text:
        if char in translit_dict:
            result += translit_dict[char]
        else:
            result += char
    
    return result


def create_unique_slug(text, model_class, instance=None, slug_field='slug', fallback_prefix='item'):
    """
    Создает уникальный slug для модели
    
    Args:
        text (str): Исходный текст для создания slug
        model_class: Класс модели Django
        instance: Экземпляр модели (для исключения при редактировании)
        slug_field (str): Название поля slug в модели
        fallback_prefix (str): Префикс для случайного slug если текст пустой
    
    Returns:
        str: Уникальный slug
    """
    
    # Транслитерируем текст
    transliterated = transliterate_russian(text)
    
    # Создаем базовый slug
    base_slug = slugify(transliterated)
    
    # Если slug пустой, создаем случайный
    if not base_slug:
        base_slug = f'{fallback_prefix}-{uuid.uuid4().hex[:8]}'
    
    # Проверяем уникальность
    slug = base_slug
    counter = 1
    
    # Создаем queryset для проверки уникальности
    queryset = model_class.objects.all()
    if instance and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    
    # Ищем уникальный slug
    filter_kwargs = {slug_field: slug}
    while queryset.filter(**filter_kwargs).exists():
        slug = f'{base_slug}-{counter}'
        filter_kwargs[slug_field] = slug
        counter += 1
    
    return slug


def validate_slug(slug):
    """
    Проверяет корректность slug
    
    Args:
        slug (str): Slug для проверки
    
    Returns:
        bool: True если slug корректный
    """
    
    if not slug:
        return False
    
    # Проверяем что slug содержит только допустимые символы
    if not re.match(r'^[a-zA-Z0-9-]+$', slug):
        return False
    
    # Проверяем что slug не начинается и не заканчивается дефисом
    if slug.startswith('-') or slug.endswith('-'):
        return False
    
    # Проверяем что нет двойных дефисов
    if '--' in slug:
        return False
    
    return True


def generate_seo_friendly_slug(title, max_length=50):
    """
    Генерирует SEO-дружественный slug
    
    Args:
        title (str): Заголовок
        max_length (int): Максимальная длина slug
    
    Returns:
        str: SEO-дружественный slug
    """
    
    # Транслитерируем
    transliterated = transliterate_russian(title)
    
    # Создаем slug
    slug = slugify(transliterated)
    
    # Обрезаем до максимальной длины
    if len(slug) > max_length:
        # Обрезаем по словам
        words = slug.split('-')
        result = ''
        for word in words:
            if len(result + '-' + word) <= max_length:
                if result:
                    result += '-'
                result += word
            else:
                break
        slug = result or slug[:max_length].rstrip('-')
    
    return slug


# Словарь часто используемых сокращений для SEO
SEO_ABBREVIATIONS = {
    'machine learning': 'ml',
    'artificial intelligence': 'ai',
    'natural language processing': 'nlp',
    'deep learning': 'dl',
    'computer vision': 'cv',
    'data science': 'ds',
    'программирование': 'programming',
    'машинное обучение': 'ml',
    'искусственный интеллект': 'ai',
    'обработка естественного языка': 'nlp',
    'глубокое обучение': 'dl',
    'компьютерное зрение': 'cv',
    'наука о данных': 'ds',
}


def apply_seo_abbreviations(text):
    """
    Применяет SEO-сокращения к тексту
    
    Args:
        text (str): Исходный текст
    
    Returns:
        str: Текст с примененными сокращениями
    """
    
    result = text.lower()
    
    for full_term, abbrev in SEO_ABBREVIATIONS.items():
        result = result.replace(full_term, abbrev)
    
    return result