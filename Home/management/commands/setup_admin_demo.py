from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Настраивает демо-данные для админ-панели'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-groups',
            action='store_true',
            help='Пропустить создание групп',
        )
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Пропустить создание тестовых данных',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Настройка демо-данных для админ-панели...'))

        # Создаем группы если не пропускаем
        if not options['skip_groups']:
            self.stdout.write(self.style.SUCCESS('📝 Создание групп пользователей...'))
            call_command('setup_admin_groups')

        # Создаем тестовые данные если не пропускаем
        if not options['skip_data']:
            self.stdout.write(self.style.SUCCESS('📊 Создание тестовых данных...'))
            call_command('create_simple_data')

        # Создаем базовые настройки сайта
        self.stdout.write(self.style.SUCCESS('⚙️ Настройка сайта...'))
        call_command('create_site_settings')

        # Создаем демо-пользователей для разных ролей
        demo_users = [
            {
                'username': 'editor',
                'email': 'editor@nlpers.ru',
                'password': 'demo123',
                'groups': ['Редакторы'],
                'is_staff': True,
                'first_name': 'Иван',
                'last_name': 'Редактор'
            },
            {
                'username': 'moderator',
                'email': 'moderator@nlpers.ru',
                'password': 'demo123',
                'groups': ['Модераторы'],
                'is_staff': True,
                'first_name': 'Мария',
                'last_name': 'Модератор'
            },
            {
                'username': 'author',
                'email': 'author@nlpers.ru',
                'password': 'demo123',
                'groups': ['Авторы'],
                'is_staff': True,
                'first_name': 'Петр',
                'last_name': 'Автор'
            }
        ]

        created_users = 0
        for user_data in demo_users:
            username = user_data['username']
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_staff=user_data['is_staff']
                )
                
                # Добавляем в группы
                for group_name in user_data['groups']:
                    try:
                        group = Group.objects.get(name=group_name)
                        user.groups.add(group)
                    except Group.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'  ⚠️ Группа не найдена: {group_name}'))
                
                self.stdout.write(self.style.SUCCESS(f'✅ Создан пользователь: {username} ({user_data["first_name"]} {user_data["last_name"]})'))
                created_users += 1
            else:
                self.stdout.write(self.style.WARNING(f'Пользователь "{username}" уже существует'))

        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('🎉 Настройка админ-панели завершена!'))
        self.stdout.write(self.style.SUCCESS(f'👥 Создано новых пользователей: {created_users}'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('🔑 Данные для входа в админ-панель:'))
        self.stdout.write(self.style.SUCCESS(''))
        
        if User.objects.filter(username='admins').exists():
            self.stdout.write(self.style.SUCCESS('   🔥 Суперадмин: admins / [ваш пароль]'))
        
        for user_data in demo_users:
            if User.objects.filter(username=user_data['username']).exists():
                roles = ', '.join(user_data['groups'])
                self.stdout.write(self.style.SUCCESS(f'   👤 {user_data["username"]} / demo123 ({roles})'))
        
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('🌐 Админ-панель доступна по адресу: http://127.0.0.1:8000/admin/'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('📋 Доступные функции:'))
        self.stdout.write(self.style.SUCCESS('   • Управление постами и категориями блога'))
        self.stdout.write(self.style.SUCCESS('   • Модерация комментариев'))
        self.stdout.write(self.style.SUCCESS('   • Управление пользователями и группами'))
        self.stdout.write(self.style.SUCCESS('   • Настройки внешнего вида сайта'))
        self.stdout.write(self.style.SUCCESS('   • Статистика и аналитика'))
        self.stdout.write(self.style.SUCCESS('   • Управление файлами архива'))