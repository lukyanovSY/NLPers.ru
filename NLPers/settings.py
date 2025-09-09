import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-08nmj643^1bv3s059#2z-cq34@ofqy*eo20q-09fve601ik9@7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['nlpers.ru', '127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django_ckeditor_5',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Кэширование и производительность
    'cachalot',
    'silk',
    'django_extensions',
    # Приложения проекта
    'Home.apps.HomeConfig',
    'Blog.apps.BlogConfig',
    'Archive.apps.ArchiveConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',  # Кэширование
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # Кэширование
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware',  # Мониторинг производительности
]

ROOT_URLCONF = 'NLPers.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'Home.context_processors.site_settings',
                'Home.context_processors.maintenance_check',
            ],
        },
    },
]

WSGI_APPLICATION = 'NLPers.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Русификация и временная зона .
LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Статика и медиафайлы
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_URL = "/static/"

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Медиа файлы - улучшенная структура
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Папки для разных типов медиа файлов
MEDIA_UPLOADS = os.path.join(MEDIA_ROOT, 'uploads')
MEDIA_IMAGES = os.path.join(MEDIA_ROOT, 'images')
MEDIA_DOCUMENTS = os.path.join(MEDIA_ROOT, 'documents')
MEDIA_VIDEOS = os.path.join(MEDIA_ROOT, 'videos')
MEDIA_AUDIO = os.path.join(MEDIA_ROOT, 'audio')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки для django-ckeditor-5
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': [
                'heading', '|', 'bold', 'italic', 'link',
                'bulletedList', 'numberedList', 'blockQuote', 'imageUpload',
            ]
        },
        'language': 'ru',
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': {
            'items': [
                'heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                'insertTable',
            ],
            'shouldNotGroupWhenFull': 'true'
        },
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        },
        'language': 'ru',
    }
}

CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"

JAZZMIN_SETTINGS = {
    "site_title": "IdealImage.ru",
    "site_header": "IdealImage.ru",
    "site_brand": "IdealImage.ru",
    "site_icon": "images/favicon.png",
    # Добавьте сюда свой собственный бренд
    "site_logo": None,
    "welcome_sign": "Welcome to the IdealImage.ru",
    # Авторские права на нижний колонтитул
    "copyright": "IdealImage.ru",
    "user_avatar": None,
    ############
    # Top Menu #
    ############
    # Ссылки для размещения в верхнем меню
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        #Url-адрес, который становится обратным (можно добавить разрешения)
        {"name": "IdealImage.ru", "url": "home", "permissions": ["auth.view_user"]},
        # model admin to link to (Permissions checked against model)
        #ссылка на администратора модели (права доступа проверены для модели)
        {"model": "auth.User"},
    ],
    #############
    # Side Menu #
    #############
    # Следует ли отображать боковое меню
    "show_sidebar": True,
    # Следует ли автоматически раскрывать меню
    "navigation_expanded": True,
    # Пользовательские значки для приложений/моделей бокового меню Смотрите здесь
    #  https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # полный список бесплатных классов иконок версии 5.13.0
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        'users.User': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'admin.LogEntry': 'fas fa-file',
    },
    # # Значки, которые используются, если они не заданы вручную
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-arrow-circle-right',
    #################
    # Related Modal #
    #################
    # Используйте модели вместо всплывающих окон
    'related_modal_active': False,
    #############
    # UI Tweaks #
    #############
    # Относительные пути к пользовательским CSS/JS скриптам (должны присутствовать в статических файлах)
    # Раскомментируйте эту строки после создания файла bootstrap-dark.css
    # 'custom_css': 'css/bootstrap-dark.css',
    'custom_js': None,
    # Следует ли отображать настройщик пользовательского интерфейса на боковой панели
    'show_ui_builder': False,
    ###############
    # Change view #
    ###############
    'changeform_format': 'horizontal_tabs',
    # переопределение форм изменения для каждого администратора модели
    'changeform_format_overrides': {
        'auth.user': 'collapsible',
        'auth.group': 'vertical_tabs',
    },
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-success',
    'accent': 'accent-teal',
    'navbar': 'navbar-dark',
    'no_navbar_border': False,
    'navbar_fixed': False,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': False,
    'sidebar': 'sidebar-dark-info',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': False,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'slate',
    'dark_mode_theme': None,
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
}

# Настройки аутентификации
LOGIN_URL = '/blog/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Настройки сессий
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 недели

# ===============================
# НАСТРОЙКИ КЭШИРОВАНИЯ
# ===============================

# Кэширование (локальное для разработки, Redis для продакшена)
if DEBUG:
    # Локальное кэширование для разработки
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake-sessions',
            'TIMEOUT': 1209600,
        }
    }
else:
    # Redis кэширование для продакшена
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                }
            },
            'KEY_PREFIX': 'nlpers',
            'TIMEOUT': 300,  # 5 минут по умолчанию
        },
        'sessions': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/2',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'nlpers_sessions',
            'TIMEOUT': 1209600,  # 2 недели
        }
    }

# Использование Redis для сессий
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# Настройки кэширования страниц
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300  # 5 минут
CACHE_MIDDLEWARE_KEY_PREFIX = 'nlpers_pages'

# Настройки django-cachalot (автоматическое кэширование ORM)
CACHALOT_ENABLED = True
CACHALOT_CACHE = 'default'
CACHALOT_TIMEOUT = 300  # 5 минут
CACHALOT_ONLY_CACHABLE_TABLES = frozenset([
    'blog_category',
    'blog_tag', 
    'home_sitesettings',
    'archive_filecategory',
])

# ===============================
# НАСТРОЙКИ ОПТИМИЗАЦИИ
# ===============================

# Настройки для django-debug-toolbar (только в DEBUG режиме)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TEMPLATE_CONTEXT': True,
        'SHOW_COLLAPSED': True,
    }

# Настройки для django-silk
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_META = True
SILKY_INTERCEPT_PERCENT = 100  # Профилировать все запросы в DEBUG режиме

# ===============================
# НАСТРОЙКИ БАЗЫ ДАННЫХ
# ===============================

# Оптимизация подключений к БД
DATABASES['default'].update({
    'CONN_MAX_AGE': 60,  # Переиспользование подключений
    'OPTIONS': {
        # SQLite не поддерживает charset и init_command
        'timeout': 20,
    }
})

# ===============================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# ===============================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'nlpers': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
