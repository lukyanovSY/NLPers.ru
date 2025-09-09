from django.core.management.base import BaseCommand
from Blog.models import Post, Category
import re
import uuid


class Command(BaseCommand):
    help = 'Исправляет slug-и для корректной работы URL'

    def transliterate(self, text):
        """Транслитерация русского текста в латиницу"""
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
        
        result = ''
        for char in text:
            if char in translit_dict:
                result += translit_dict[char]
            else:
                result += char
        return result

    def create_slug(self, title):
        """Создает slug из заголовка"""
        # Транслитерируем
        transliterated = self.transliterate(title)
        
        # Приводим к нижнему регистру
        slug = transliterated.lower()
        
        # Заменяем пробелы и специальные символы на дефисы
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # Убираем дефисы в начале и конце
        slug = slug.strip('-')
        
        # Если slug пустой, создаем случайный
        if not slug:
            slug = f'post-{uuid.uuid4().hex[:8]}'
        
        return slug

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Исправление slug-ов...'))
        
        # Исправляем slug-и постов
        posts = Post.objects.all()
        for post in posts:
            old_slug = post.slug
            new_slug = self.create_slug(post.title)
            
            # Проверяем уникальность
            counter = 1
            original_slug = new_slug
            while Post.objects.filter(slug=new_slug).exclude(id=post.id).exists():
                new_slug = f'{original_slug}-{counter}'
                counter += 1
            
            if old_slug != new_slug:
                post.slug = new_slug
                post.save(update_fields=['slug'])
                self.stdout.write(f'✅ Пост "{post.title}": {old_slug} -> {new_slug}')
        
        # Исправляем slug-и категорий
        categories = Category.objects.all()
        for category in categories:
            old_slug = category.slug
            new_slug = self.create_slug(category.name)
            
            # Проверяем уникальность
            counter = 1
            original_slug = new_slug
            while Category.objects.filter(slug=new_slug).exclude(id=category.id).exists():
                new_slug = f'{original_slug}-{counter}'
                counter += 1
            
            if old_slug != new_slug:
                category.slug = new_slug
                category.save(update_fields=['slug'])
                self.stdout.write(f'✅ Категория "{category.name}": {old_slug} -> {new_slug}')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Все slug-и исправлены!')
        )