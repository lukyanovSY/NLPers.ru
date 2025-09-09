**Разработка**
```bash
### upgrade pip 
python.exe -m pip install --upgrade pip

### requirements
python -m pip install -r requirements.txt
    pip freeze > requirements.txt
    pip freeze
    pip freeze --local

### Создание миграций
python manage.py makemigrations
    ### Применение миграций
    python manage.py migrate
    ### Создание резервной копии
    python manage.py dumpdata > backup.json
    ### Восстановление из резервной копии
    python manage.py loaddata backup.json

    python manage.py makemigrations tree --name add_userprofile

    python manage.py showmigrations tree

   [ python manage.py collectstatic --noinput ]
```

**VENV**
```bash
## [  venv   ] ################
   python -m venv venv
   source venv/Scripts/activate
       venv/Scripts/activate
   source .venv/python311/bin/activate   

   deactivate

## py manage.py runserver

    [ py manage.py runserver ]




## [ pip install ] ###########

    python.exe -m pip install --upgrade pip  

    pip install --upgrade Pillow --no-binary :all:

    pip install Django
                           [ "ОБРАБОТКА ИЗОБРАЖЕНИЙ"]
    pip install Pillow                 
                           [   "Древовидное меню "  ]
    pip install django-mptt
                           [    "slug переделка "    ]
    pip install pytils
                          [   "Редактор текста "   ]
    pip install django-ckeditor
                           [        "ФОРМЫ  "       ]
    pip install django-crispy-forms

    pip install django_apscheduler

    pip install Unidecode

    pip install django-taggit

    pip install aiogram

    pip install python-telegram-bot==13.15 -U

    pip install python-telegram-bot[ext] -U

    pip install python-telegram-bot[passport,socks,webhooks,http2,rate-limiter,callback-data,job-queue]

    pip install django-jazzmin

## pip install Django

    idealimage.orel@yandex.ru
    Lsy05011975

    pip install django-mptt

    pip install django-ckeditor
    settings>>
    'ckeditor','ckeditor_uploader',
    CKEDITOR_UPLOAD_PATH = "uploads/"
    urls>>
    path('ckeditor/', include('ckeditor_uploader.urls')),

    pip install pillow

    python.exe -m pip install --upgrade pip


## [ django-admin ] ##########

   django-admin startproject Project_my
   django-admin startproject Project_my .
    >[Точка в конце команды чтобы проект создался в текущей папке]
   python manage.py startapp userrss home  
    >[Project_my.settings > INSTALLED_APPS ='viza.apps.VizaConfig',]
   

## [ migrate ] ###############
   python manage.py makemigrations
   python manage.py migrate


   python manage.py createsuperuser
   [если вы забыли пароль суперпользователя, его можно сменить так:]
   python manage.py change password <имя пользователя>.

## python manage.py makemigrations
    python manage.py migrate

    python manage.py makemigrations --merge            объединить миграции


python manage.py collectstatic --noinput



>Для ситуаций, когда необходимо создать новый проект на Django с существующей базой
>данных, разработчики фреймворка создали команду 

python manage.py inspectdb

> Она возвращает содержимое models.py,
>основанное на схеме БД, и позволяет пропустить этап описания моделей вручную.
>Однако советуем не приегать к этому способу при обучении.

{{{{{{{{            python manage.py runserver            ]]]]]]]


>URLS: 

{% include "onas/doc/list_doc_lev.html" %}

git remote add origin git@github.com:lukyanovSY/NLPers.ru.git

pip install djangorestframework
