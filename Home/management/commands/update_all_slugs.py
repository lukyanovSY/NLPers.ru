from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Обновляет все slug для постов и категорий с улучшенной транслитерацией'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно обновить все slug, включая уже существующие',
        )
        parser.add_argument(
            '--categories-only',
            action='store_true',
            help='Обновить только категории',
        )
        parser.add_argument(
            '--posts-only',
            action='store_true',
            help='Обновить только посты',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет изменено без фактического обновления',
        )

    def handle(self, *args, **options):
        try:
            from Blog.models import Category, Post
            from Blog.utils import create_unique_slug
        except ImportError:
            self.stdout.write(self.style.ERROR('❌ Модели блога не найдены'))
            return

        self.stdout.write(self.style.SUCCESS('🔄 Обновление slug-ов...'))
        
        force = options['force']
        categories_only = options['categories_only']
        posts_only = options['posts_only']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('📋 Режим симуляции - изменения не будут сохранены'))

        updated_categories = 0
        updated_posts = 0

        # Обновляем категории
        if not posts_only:
            self.stdout.write(self.style.SUCCESS('\n📁 Обновление категорий...'))
            
            categories = Category.objects.all()
            for category in categories:
                old_slug = category.slug
                
                # Создаем новый slug
                new_slug = create_unique_slug(
                    category.name, 
                    Category, 
                    instance=category,
                    fallback_prefix='category'
                )
                
                # Проверяем нужно ли обновлять
                needs_update = force or not old_slug or old_slug != new_slug or not self.is_latin_slug(old_slug)
                
                if needs_update:
                    if dry_run:
                        self.stdout.write(
                            f'  📝 {category.name}: "{old_slug}" → "{new_slug}"'
                        )
                    else:
                        try:
                            with transaction.atomic():
                                category.slug = new_slug
                                category.save(update_fields=['slug'])
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✅ {category.name}: "{old_slug}" → "{new_slug}"')
                                )
                                updated_categories += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'  ❌ Ошибка при обновлении {category.name}: {e}')
                            )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ⏭️ {category.name}: slug уже корректный')
                    )

        # Обновляем посты
        if not categories_only:
            self.stdout.write(self.style.SUCCESS('\n📝 Обновление постов...'))
            
            posts = Post.objects.all()
            for post in posts:
                old_slug = post.slug
                
                # Создаем новый slug
                new_slug = create_unique_slug(
                    post.title, 
                    Post, 
                    instance=post,
                    fallback_prefix='post'
                )
                
                # Проверяем нужно ли обновлять
                needs_update = force or not old_slug or old_slug != new_slug or not self.is_latin_slug(old_slug)
                
                if needs_update:
                    if dry_run:
                        self.stdout.write(
                            f'  📝 {post.title}: "{old_slug}" → "{new_slug}"'
                        )
                    else:
                        try:
                            with transaction.atomic():
                                post.slug = new_slug
                                post.save(update_fields=['slug'])
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✅ {post.title}: "{old_slug}" → "{new_slug}"')
                                )
                                updated_posts += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'  ❌ Ошибка при обновлении {post.title}: {e}')
                            )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ⏭️ {post.title}: slug уже корректный')
                    )

        # Итоги
        self.stdout.write(self.style.SUCCESS('\n🎉 Обновление завершено!'))
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'📊 Статистика:'))
            if not posts_only:
                self.stdout.write(self.style.SUCCESS(f'   📁 Обновлено категорий: {updated_categories}'))
            if not categories_only:
                self.stdout.write(self.style.SUCCESS(f'   📝 Обновлено постов: {updated_posts}'))
        else:
            self.stdout.write(self.style.WARNING('💡 Для фактического обновления запустите команду без --dry-run'))

        self.stdout.write(self.style.SUCCESS('\n🔗 Преимущества новых slug:'))
        self.stdout.write(self.style.SUCCESS('   • Правильная транслитерация русских букв'))
        self.stdout.write(self.style.SUCCESS('   • Уникальность всех slug'))
        self.stdout.write(self.style.SUCCESS('   • SEO-дружественные URL'))
        self.stdout.write(self.style.SUCCESS('   • Читаемые адреса на латинице'))

    def is_latin_slug(self, slug):
        """Проверяет содержит ли slug только латинские символы"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9-]+$', slug)) if slug else False