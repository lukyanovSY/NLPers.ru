from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Создает группы пользователей и настраивает права доступа для админ-панели'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔐 Настройка групп пользователей и прав доступа...'))

        # Создаем группы
        groups_config = {
            'Редакторы': {
                'description': 'Могут создавать и редактировать контент',
                'permissions': [
                    # Blog permissions
                    'Blog.add_post', 'Blog.change_post', 'Blog.view_post',
                    'Blog.add_category', 'Blog.change_category', 'Blog.view_category',
                    'Blog.add_comment', 'Blog.change_comment', 'Blog.view_comment',
                    'Blog.view_userprofile', 'Blog.change_userprofile',
                    # Archive permissions
                    'Archive.add_archivefile', 'Archive.change_archivefile', 'Archive.view_archivefile',
                    'Archive.add_filecategory', 'Archive.change_filecategory', 'Archive.view_filecategory',
                ]
            },
            'Модераторы': {
                'description': 'Могут модерировать контент и управлять пользователями',
                'permissions': [
                    # Все права редакторов плюс дополнительные
                    'Blog.delete_comment', 'Blog.change_comment',
                    'auth.view_user', 'auth.change_user',
                    'Blog.view_like', 'Blog.view_follow',
                ]
            },
            'Авторы': {
                'description': 'Могут создавать свои посты',
                'permissions': [
                    'Blog.add_post', 'Blog.view_post',
                    'Blog.view_category',
                    'Blog.add_comment', 'Blog.view_comment',
                    'Blog.view_userprofile', 'Blog.change_userprofile',
                ]
            },
            'Менеджеры контента': {
                'description': 'Полный доступ к контенту, но без системных настроек',
                'permissions': [
                    # Все права блога
                    'Blog.add_post', 'Blog.change_post', 'Blog.delete_post', 'Blog.view_post',
                    'Blog.add_category', 'Blog.change_category', 'Blog.delete_category', 'Blog.view_category',
                    'Blog.add_comment', 'Blog.change_comment', 'Blog.delete_comment', 'Blog.view_comment',
                    'Blog.view_userprofile', 'Blog.change_userprofile',
                    'Blog.view_like', 'Blog.change_like', 'Blog.delete_like',
                    'Blog.view_follow', 'Blog.change_follow', 'Blog.delete_follow',
                    'Blog.view_newsletter', 'Blog.change_newsletter', 'Blog.delete_newsletter',
                    # Права архива
                    'Archive.add_archivefile', 'Archive.change_archivefile', 'Archive.delete_archivefile', 'Archive.view_archivefile',
                    'Archive.add_filecategory', 'Archive.change_filecategory', 'Archive.delete_filecategory', 'Archive.view_filecategory',
                    # Настройки сайта
                    'Home.view_sitesettings', 'Home.change_sitesettings',
                ]
            }
        }

        created_groups = 0
        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Создана группа: {group_name}'))
                created_groups += 1
            else:
                self.stdout.write(self.style.WARNING(f'Группа "{group_name}" уже существует'))

            # Добавляем разрешения
            permissions_added = 0
            for perm_code in config['permissions']:
                try:
                    app_label, codename = perm_code.split('.')
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    if not group.permissions.filter(id=permission.id).exists():
                        group.permissions.add(permission)
                        permissions_added += 1
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ Разрешение не найдено: {perm_code}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ Ошибка с разрешением {perm_code}: {e}'))

            if permissions_added > 0:
                self.stdout.write(self.style.SUCCESS(f'  📝 Добавлено разрешений: {permissions_added}'))

        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('🎉 Настройка групп завершена!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Создано новых групп: {created_groups}'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('💡 Созданные группы:'))
        for group_name, config in groups_config.items():
            self.stdout.write(self.style.SUCCESS(f'   👥 {group_name}: {config["description"]}'))
        
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('🔧 Для назначения пользователей в группы:'))
        self.stdout.write(self.style.SUCCESS('   1. Перейдите в админку (/admin/)'))
        self.stdout.write(self.style.SUCCESS('   2. Откройте "Пользователи"'))
        self.stdout.write(self.style.SUCCESS('   3. Выберите пользователя'))
        self.stdout.write(self.style.SUCCESS('   4. В разделе "Разрешения" добавьте нужные группы'))