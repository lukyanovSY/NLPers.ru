from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Blog.models import Category, Post
from django.utils import timezone


class Command(BaseCommand):
    help = 'Создает базовые тестовые данные для блога'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Создание базовых тестовых данных...'))
        
        # Создаем простые категории
        categories_data = [
            {'name': 'Программирование', 'slug': 'programming'},
            {'name': 'Python', 'slug': 'python'},
            {'name': 'Django', 'slug': 'django'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'description': f'Категория {cat_data["name"]}'}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'✅ Создана категория: {category.name}')
        
        # Создаем тестового пользователя
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь',
                'is_active': True
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(f'✅ Создан пользователь: {user.username}')
        
        # Создаем простые тестовые посты
        posts_data = [
            {
                'title': 'Добро пожаловать в блог NLPers.ru!',
                'content': '<h2>Привет!</h2><p>Это первый пост в нашем блоге. Здесь мы будем делиться знаниями о программировании, Python и Django.</p>',
                'excerpt': 'Добро пожаловать в наш блог о программировании и технологиях.',
                'category_index': 0
            },
            {
                'title': 'Основы Python для начинающих',
                'content': '<h2>Python - отличный язык!</h2><p>Python простой в изучении и мощный язык программирования.</p><pre><code>print("Hello, World!")</code></pre>',
                'excerpt': 'Изучаем основы Python - простого и мощного языка программирования.',
                'category_index': 1
            },
            {
                'title': 'Создание веб-приложений на Django',
                'content': '<h2>Django Framework</h2><p>Django позволяет быстро создавать веб-приложения на Python.</p>',
                'excerpt': 'Учимся создавать веб-приложения с помощью Django фреймворка.',
                'category_index': 2
            }
        ]
        
        for i, post_data in enumerate(posts_data):
            category = categories[post_data['category_index']]
            
            post, created = Post.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'content': post_data['content'],
                    'excerpt': post_data['excerpt'],
                    'author': user,
                    'category': category,
                    'slug': post_data['title'].lower().replace(' ', '-').replace('!', '').replace(',', ''),
                    'status': 'published',
                    'published_at': timezone.now(),
                    'views_count': 10 + i * 5,
                    'likes_count': i + 1,
                    'reading_time': 3 + i,
                    'is_featured': i == 0,  # Первый пост рекомендуемый
                    'allow_comments': True
                }
            )
            if created:
                self.stdout.write(f'✅ Создан пост: {post.title}')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Базовые тестовые данные созданы!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📁 Создано категорий: {len(categories)}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📝 Создано постов: {Post.objects.count()}')
        )
        self.stdout.write(
            self.style.WARNING('🔑 Для входа: testuser / demo123')
        )