from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Blog.models import Category, Post, UserProfile, Comment
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Создает тестовые данные для блога'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Создание тестовых данных для блога...'))
        
        # Создаем категории
        categories_data = [
            {
                'name': 'Программирование',
                'slug': 'programming',
                'description': 'Статьи о программировании и разработке программного обеспечения'
            },
            {
                'name': 'Искусственный интеллект',
                'slug': 'ai',
                'description': 'Материалы по машинному обучению, нейронным сетям и ИИ'
            },
            {
                'name': 'Веб-разработка',
                'slug': 'web-development',
                'description': 'Фронтенд, бэкенд и полный стек веб-разработки'
            },
            {
                'name': 'Data Science',
                'slug': 'data-science',
                'description': 'Анализ данных, визуализация и наука о данных'
            },
            {
                'name': 'Python',
                'slug': 'python',
                'description': 'Всё о языке программирования Python'
            },
            {
                'name': 'Туториалы',
                'slug': 'tutorials',
                'description': 'Пошаговые руководства и обучающие материалы'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'✅ Создана категория: {category.name}')
        
        # Создаем тестовых пользователей
        users_data = [
            {
                'username': 'ivan_petrov',
                'email': 'ivan@example.com',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'bio': 'Senior Python Developer с 7-летним опытом. Специализируюсь на Django, FastAPI и машинном обучении. Люблю делиться знаниями и помогать начинающим разработчикам.',
                'location': 'Москва, Россия'
            },
            {
                'username': 'maria_data',
                'email': 'maria@example.com',
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'bio': 'Data Scientist и исследователь в области NLP. PhD в области компьютерных наук. Работаю с большими данными и создаю ML-модели для анализа текста.',
                'location': 'Санкт-Петербург, Россия'
            },
            {
                'username': 'alex_fullstack',
                'email': 'alex@example.com',
                'first_name': 'Алексей',
                'last_name': 'Козлов',
                'bio': 'Full-stack разработчик. Создаю современные веб-приложения на React + Django. Увлекаюсь DevOps и облачными технологиями.',
                'location': 'Казань, Россия'
            }
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(f'✅ Создан пользователь: {user.username}')
            
            # Создаем профиль
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': user_data['bio'],
                    'location': user_data['location'],
                    'is_verified': True
                }
            )
            users.append(user)
        
        # Создаем тестовые посты
        posts_data = [
            {
                'title': 'Полное руководство по Django: От новичка до профессионала',
                'content': '''
                <h2>🚀 Введение в Django</h2>
                <p>Django - это высокоуровневый веб-фреймворк для Python, который позволяет быстро создавать безопасные и масштабируемые веб-приложения. В этом руководстве мы изучим Django от основ до продвинутых концепций.</p>
                
                <h3>📦 Установка и настройка</h3>
                <p>Начнем с установки Django:</p>
                <pre><code class="language-bash">pip install django
django-admin startproject myproject
cd myproject
python manage.py runserver</code></pre>
                
                <h3>🏗️ Архитектура Django</h3>
                <p>Django следует паттерну MTV (Model-Template-View):</p>
                <ul>
                    <li><strong>Model</strong> - работа с данными и бизнес-логика</li>
                    <li><strong>Template</strong> - представление данных пользователю</li>
                    <li><strong>View</strong> - обработка запросов и подготовка данных</li>
                </ul>
                
                <h3>🔧 Создание первого приложения</h3>
                <pre><code class="language-python">from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title</code></pre>
        
                <p>Django - мощный инструмент для создания веб-приложений. Следуя принципам DRY (Don't Repeat Yourself) и convention over configuration, он позволяет сосредоточиться на бизнес-логике.</p>
                ''',
                'excerpt': 'Изучаем Django с нуля: установка, архитектура, создание моделей и views. Полное руководство для начинающих и продвинутых разработчиков.',
                'tags': 'Django, Python, Веб-разработка, Backend, Framework',
                'category_index': 0,  # Программирование
                'reading_time': 15
            },
            {
                'title': 'Машинное обучение с Python: Практическое руководство',
                'content': '''
                <h2>🤖 Введение в машинное обучение</h2>
                <p>Машинное обучение - это область искусственного интеллекта, которая позволяет компьютерам обучаться и делать предсказания без явного программирования каждого случая.</p>
                
                <h3>📚 Основные библиотеки</h3>
                <p>Для работы с ML в Python используются следующие библиотеки:</p>
                <ul>
                    <li><strong>NumPy</strong> - работа с массивами и математические операции</li>
                    <li><strong>Pandas</strong> - анализ и обработка данных</li>
                    <li><strong>Scikit-learn</strong> - алгоритмы машинного обучения</li>
                    <li><strong>Matplotlib/Seaborn</strong> - визуализация данных</li>
                </ul>
                
                <h3>🔄 Процесс машинного обучения</h3>
                <pre><code class="language-python">import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Загрузка данных
data = pd.read_csv('dataset.csv')

# Разделение на признаки и целевую переменную
X = data.drop('target', axis=1)
y = data['target']

# Разделение на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создание и обучение модели
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Предсказания и оценка
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f'Точность модели: {accuracy:.2%}')</code></pre>

                <h3>📊 Типы задач машинного обучения</h3>
                <p>Основные типы задач:</p>
                <ul>
                    <li><strong>Классификация</strong> - предсказание категории</li>
                    <li><strong>Регрессия</strong> - предсказание числового значения</li>
                    <li><strong>Кластеризация</strong> - группировка похожих объектов</li>
                </ul>
                
                <p>Машинное обучение открывает огромные возможности для анализа данных и автоматизации принятия решений.</p>
                ''',
                'excerpt': 'Практическое введение в машинное обучение с Python. Изучаем основные библиотеки, алгоритмы и создаем первые ML-модели.',
                'tags': 'Machine Learning, Python, AI, Scikit-learn, Data Science',
                'category_index': 1,  # ИИ
                'reading_time': 20
            },
            {
                'title': 'React + Django: Создаем современное SPA приложение',
                'content': '''
                <h2>⚛️ Современный стек разработки</h2>
                <p>Комбинация React на фронтенде и Django REST Framework на бэкенде - мощное решение для создания современных веб-приложений.</p>
                
                <h3>🛠️ Настройка Django REST API</h3>
                <p>Начнем с создания API на Django:</p>
                <pre><code class="language-python"># settings.py
INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    # ваши приложения
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # другие middleware
]

# Настройки CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
]

# Настройки DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}</code></pre>

                <h3>📡 Создание API endpoints</h3>
                <pre><code class="language-python"># serializers.py
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'excerpt', 'author_name', 'created_at']

# views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_posts = self.queryset.filter(is_featured=True)[:3]
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)</code></pre>

                <h3>⚛️ React компоненты</h3>
                <pre><code class="language-jsx">// PostList.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PostList = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await axios.get('/api/posts/');
        setPosts(response.data.results);
      } catch (error) {
        console.error('Ошибка загрузки постов:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="post-list">
      {posts.map(post => (
        <div key={post.id} className="post-card">
          <h3>{post.title}</h3>
          <p>{post.excerpt}</p>
          <small>Автор: {post.author_name}</small>
        </div>
      ))}
    </div>
  );
};

export default PostList;</code></pre>

                <p>Такой подход позволяет создавать быстрые, интерактивные приложения с четким разделением фронтенда и бэкенда.</p>
                ''',
                'excerpt': 'Создаем современное SPA приложение используя React и Django REST Framework. API, компоненты, аутентификация.',
                'tags': 'React, Django, REST API, SPA, JavaScript, Full-stack',
                'category_index': 2,  # Веб-разработка
                'reading_time': 25
            },
            {
                'title': 'Анализ данных с Pandas: От загрузки до визуализации',
                'content': '''
                <h2>📊 Pandas для анализа данных</h2>
                <p>Pandas - фундаментальная библиотека для анализа данных в Python. Она предоставляет мощные инструменты для работы с структурированными данными.</p>
                
                <h3>📁 Загрузка и изучение данных</h3>
                <pre><code class="language-python">import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузка данных из различных источников
df_csv = pd.read_csv('data.csv')
df_excel = pd.read_excel('data.xlsx')
df_json = pd.read_json('data.json')

# Первичное изучение данных
print(f"Размер датасета: {df.shape}")
print(f"\\nИнформация о данных:")
print(df.info())
print(f"\\nПервые 5 строк:")
print(df.head())
print(f"\\nСтатистическое описание:")
print(df.describe())</code></pre>

                <h3>🧹 Очистка и подготовка данных</h3>
                <pre><code class="language-python"># Проверка пропущенных значений
missing_data = df.isnull().sum()
print("Пропущенные значения:", missing_data[missing_data > 0])

# Заполнение пропущенных значений
df['column'].fillna(df['column'].mean(), inplace=True)

# Удаление дубликатов
df.drop_duplicates(inplace=True)

# Преобразование типов данных
df['date_column'] = pd.to_datetime(df['date_column'])
df['category'] = df['category'].astype('category')

# Создание новых признаков
df['year'] = df['date_column'].dt.year
df['month'] = df['date_column'].dt.month</code></pre>

                <h3>🔍 Анализ и группировка</h3>
                <pre><code class="language-python"># Группировка и агрегация
grouped = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'count'],
    'profit': ['sum', 'mean']
})

# Фильтрация данных
high_sales = df[df['sales'] > df['sales'].quantile(0.9)]

# Сводные таблицы
pivot_table = df.pivot_table(
    values='sales',
    index='category',
    columns='region',
    aggfunc='sum'
)

# Корреляционный анализ
correlation_matrix = df.select_dtypes(include=[np.number]).corr()
print(correlation_matrix)</code></pre>

                <h3>📈 Визуализация результатов</h3>
                <pre><code class="language-python"># Настройка стиля
plt.style.use('seaborn-v0_8')
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Гистограмма
df['sales'].hist(bins=30, ax=axes[0,0])
axes[0,0].set_title('Распределение продаж')

# Точечная диаграмма
axes[0,1].scatter(df['advertising'], df['sales'])
axes[0,1].set_xlabel('Расходы на рекламу')
axes[0,1].set_ylabel('Продажи')

# Тепловая карта корреляций
sns.heatmap(correlation_matrix, annot=True, ax=axes[1,0])
axes[1,0].set_title('Матрица корреляций')

# Временной ряд
df.groupby('date')['sales'].sum().plot(ax=axes[1,1])
axes[1,1].set_title('Продажи по времени')

plt.tight_layout()
plt.show()</code></pre>

                <p>Pandas открывает безграничные возможности для анализа данных, от простой статистики до сложных исследований.</p>
                ''',
                'excerpt': 'Полное руководство по анализу данных с Pandas: загрузка, очистка, анализ и визуализация. Практические примеры.',
                'tags': 'Pandas, Data Science, Python, Анализ данных, Визуализация',
                'category_index': 3,  # Data Science
                'reading_time': 18
            },
            {
                'title': 'Python для начинающих: Основы программирования',
                'content': '''
                <h2>🐍 Добро пожаловать в мир Python!</h2>
                <p>Python - один из самых популярных и дружелюбных языков программирования. Его простой синтаксис и мощные возможности делают его идеальным для начинающих.</p>
                
                <h3>🚀 Первые шаги</h3>
                <pre><code class="language-python"># Ваша первая программа
print("Привет, мир!")

# Переменные и типы данных
name = "Анна"           # строка
age = 25               # целое число
height = 165.5         # число с плавающей точкой
is_student = True      # булево значение

# Вывод информации
print(f"Меня зовут {name}, мне {age} лет")
print(f"Мой рост: {height} см")</code></pre>

                <h3>📝 Работа со структурами данных</h3>
                <pre><code class="language-python"># Списки - упорядоченные коллекции
fruits = ["яблоко", "банан", "апельсин"]
fruits.append("груша")
print(f"Фруктов в списке: {len(fruits)}")

# Словари - пары ключ-значение
person = {
    "name": "Иван",
    "age": 30,
    "city": "Москва"
}
print(f"Возраст: {person['age']}")

# Множества - уникальные элементы
numbers = {1, 2, 3, 3, 4, 5}
print(f"Уникальные числа: {numbers}")</code></pre>

                <h3>🔄 Циклы и условия</h3>
                <pre><code class="language-python"># Условные конструкции
temperature = 25

if temperature > 30:
    print("Жарко!")
elif temperature > 20:
    print("Тепло")
else:
    print("Холодно")

# Цикл for
for fruit in fruits:
    print(f"Мне нравится {fruit}")

# Цикл while
count = 0
while count < 3:
    print(f"Счет: {count}")
    count += 1

# Генераторы списков
squares = [x**2 for x in range(1, 6)]
print(f"Квадраты: {squares}")</code></pre>

                <h3>🔧 Функции</h3>
                <pre><code class="language-python"># Определение функции
def greet(name, greeting="Привет"):
    return f"{greeting}, {name}!"

# Использование функции
message = greet("Мария")
print(message)

# Функция с несколькими параметрами
def calculate_area(length, width):
    """Вычисляет площадь прямоугольника"""
    area = length * width
    return area

rectangle_area = calculate_area(10, 5)
print(f"Площадь: {rectangle_area} кв.м")</code></pre>

                <h3>📚 Работа с файлами</h3>
                <pre><code class="language-python"># Чтение файла
try:
    with open('data.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        print(content)
except FileNotFoundError:
    print("Файл не найден")

# Запись в файл
data = ["строка 1", "строка 2", "строка 3"]
with open('output.txt', 'w', encoding='utf-8') as file:
    for line in data:
        file.write(line + '\\n')</code></pre>

                <p>Python - это лишь начало увлекательного путешествия в мир программирования. Изучайте, практикуйтесь и создавайте!</p>
                ''',
                'excerpt': 'Изучаем основы Python: переменные, циклы, функции, работа с файлами. Идеально для начинающих программистов.',
                'tags': 'Python, Программирование, Основы, Туториал, Начинающим',
                'category_index': 4,  # Python
                'reading_time': 12
            }
        ]
        
        # Создаем посты
        for i, post_data in enumerate(posts_data):
            author = users[i % len(users)]
            category = categories[post_data['category_index']]
            
            post, created = Post.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'content': post_data['content'],
                    'excerpt': post_data['excerpt'],
                    'tags': post_data['tags'],
                    'author': author,
                    'category': category,
                    'slug': post_data['title'].lower().replace(' ', '-').replace(':', '').replace(',', '').replace('(', '').replace(')', ''),
                    'status': 'published',
                    'published_at': timezone.now() - timezone.timedelta(days=random.randint(1, 30)),
                    'views_count': random.randint(50, 1500),
                    'likes_count': random.randint(5, 100),
                    'reading_time': post_data['reading_time'],
                    'is_featured': i < 3,  # Первые 3 поста делаем рекомендуемыми
                    'allow_comments': True
                }
            )
            if created:
                self.stdout.write(f'✅ Создан пост: {post.title[:50]}...')
        
        # Создаем комментарии
        posts = Post.objects.filter(status='published')
        comments_texts = [
            "Отличная статья! Очень полезная информация, спасибо автору!",
            "Интересный материал, особенно понравился раздел про практическое применение.",
            "Хорошо написано, но хотелось бы больше примеров кода.",
            "Спасибо за подробное объяснение! Теперь всё стало понятно.",
            "Качественный контент! Буду рекомендовать коллегам.",
            "Очень актуальная тема, жду продолжения!",
            "Полезно и понятно изложено. Сохранил в закладки.",
            "Отличный туториал! Помог решить мою проблему.",
            "Хороший обзор технологии, спасибо за труд!",
            "Интересный подход к решению задачи."
        ]
        
        for post in posts:
            # Случайное количество комментариев от 2 до 8
            num_comments = random.randint(2, 8)
            for j in range(num_comments):
                comment_author = users[j % len(users)]
                if comment_author != post.author:  # Не комментируем свои посты
                    Comment.objects.create(
                        post=post,
                        author=comment_author,
                        content=random.choice(comments_texts),
                        likes_count=random.randint(0, 20),
                        created_at=timezone.now() - timezone.timedelta(hours=random.randint(1, 168))  # До недели назад
                    )
        
        # Обновляем счетчики комментариев в постах
        for post in posts:
            post.comments_count = post.comments.count()
            post.save(update_fields=['comments_count'])
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Тестовые данные успешно созданы!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📁 Создано категорий: {len(categories)}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'👥 Создано пользователей: {len(users)}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📝 Создано постов: {posts.count()}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'💬 Создано комментариев: {Comment.objects.count()}')
        )
        
        # Информация для входа
        self.stdout.write(
            self.style.WARNING('\n🔑 Данные для входа в систему:')
        )
        for user_data in users_data:
            self.stdout.write(
                f"Пользователь: {user_data['username']} | Пароль: demo123"
            )