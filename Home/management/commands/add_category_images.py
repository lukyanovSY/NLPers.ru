from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io
import os


class Command(BaseCommand):
    help = 'Добавляет тестовые изображения к категориям блога'

    def handle(self, *args, **options):
        try:
            from Blog.models import Category
        except ImportError:
            self.stdout.write(self.style.ERROR('❌ Модель Category не найдена'))
            return

        self.stdout.write(self.style.SUCCESS('🎨 Создание тестовых изображений для категорий...'))

        # Словарь с настройками для каждой категории
        category_settings = {
            'Python': {
                'background_color': '#3776ab',
                'text_color': '#ffffff',
                'icon': '🐍'
            },
            'Django': {
                'background_color': '#092e20',
                'text_color': '#ffffff',
                'icon': '🌟'
            },
            'Machine Learning': {
                'background_color': '#ff6b6b',
                'text_color': '#ffffff',
                'icon': '🤖'
            },
            'NLP': {
                'background_color': '#4ecdc4',
                'text_color': '#ffffff',
                'icon': '📝'
            },
            'Новости': {
                'background_color': '#45b7d1',
                'text_color': '#ffffff',
                'icon': '📰'
            },
            'Обучение': {
                'background_color': '#96ceb4',
                'text_color': '#ffffff',
                'icon': '📚'
            }
        }

        updated_count = 0
        
        for category in Category.objects.all():
            # Пропускаем категории, у которых уже есть изображения
            if category.image:
                self.stdout.write(self.style.WARNING(f'⏭️ У категории "{category.name}" уже есть изображение'))
                continue

            # Получаем настройки для категории или используем дефолтные
            settings = category_settings.get(category.name, {
                'background_color': category.color or '#007bff',
                'text_color': '#ffffff',
                'icon': '📁'
            })

            # Создаем изображение
            try:
                image = self.create_category_image(
                    category.name,
                    settings['background_color'],
                    settings['text_color'],
                    settings['icon']
                )

                # Сохраняем изображение
                image_io = io.BytesIO()
                image.save(image_io, format='PNG', quality=95)
                image_file = ContentFile(image_io.getvalue())

                # Создаем имя файла
                filename = f"{category.slug}_category.png"
                
                # Сохраняем в модель
                category.image.save(filename, image_file, save=False)
                category.save()

                self.stdout.write(self.style.SUCCESS(f'✅ Создано изображение для категории "{category.name}"'))
                updated_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка при создании изображения для "{category.name}": {e}'))

        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS(f'🎉 Обработка завершена!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Обновлено категорий: {updated_count}'))
        
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(''))
            self.stdout.write(self.style.SUCCESS('💡 Рекомендации:'))
            self.stdout.write(self.style.SUCCESS('   • Зайдите в админку для проверки изображений'))
            self.stdout.write(self.style.SUCCESS('   • При необходимости загрузите собственные изображения'))
            self.stdout.write(self.style.SUCCESS('   • Размер изображений: 400x300px для лучшего качества'))

    def create_category_image(self, text, bg_color, text_color, icon):
        """Создает изображение для категории"""
        
        # Размеры изображения
        width, height = 400, 300
        
        # Создаем изображение с градиентом
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Создаем градиентный эффект
        for y in range(height):
            # Градиент от более темного сверху к более светлому снизу
            alpha = y / height
            r, g, b = self.hex_to_rgb(bg_color)
            new_r = int(r + (255 - r) * alpha * 0.2)
            new_g = int(g + (255 - g) * alpha * 0.2)
            new_b = int(b + (255 - b) * alpha * 0.2)
            
            color = (min(255, new_r), min(255, new_g), min(255, new_b))
            draw.line([(0, y), (width, y)], fill=color)
        
        # Пытаемся загрузить шрифт
        try:
            # Для иконки
            icon_font = ImageFont.truetype("arial.ttf", 60)
            text_font = ImageFont.truetype("arial.ttf", 32)
        except:
            try:
                icon_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            except:
                icon_font = None
                text_font = None
        
        # Рисуем иконку
        icon_bbox = draw.textbbox((0, 0), icon, font=icon_font)
        icon_width = icon_bbox[2] - icon_bbox[0]
        icon_height = icon_bbox[3] - icon_bbox[1]
        icon_x = (width - icon_width) // 2
        icon_y = height // 2 - 40
        
        draw.text((icon_x, icon_y), icon, fill=text_color, font=icon_font)
        
        # Рисуем текст
        if len(text) > 15:
            text = text[:12] + "..."
        
        text_bbox = draw.textbbox((0, 0), text, font=text_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = height // 2 + 20
        
        draw.text((text_x, text_y), text, fill=text_color, font=text_font)
        
        # Добавляем рамку
        draw.rectangle([(0, 0), (width-1, height-1)], outline=text_color, width=3)
        
        return image
    
    def hex_to_rgb(self, hex_color):
        """Конвертирует HEX цвет в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))