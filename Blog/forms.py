from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Post, Comment, UserProfile, Category, Newsletter, AuthorRequest


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования постов"""
    
    class Meta:
        model = Post
        fields = [
            'title', 'category', 'content', 'excerpt', 'featured_image', 
            'tags', 'status', 'is_featured', 'allow_comments'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок поста...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'content': CKEditor5Widget(attrs={
                'class': 'django_ckeditor_5'
            }, config_name='extends'),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Краткое описание поста для превью...',
                'maxlength': 300
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Python, Django, Веб-разработка'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Заголовок',
            'category': 'Категория',
            'content': 'Содержание',
            'excerpt': 'Краткое описание',
            'featured_image': 'Главное изображение',
            'tags': 'Теги',
            'status': 'Статус',
            'is_featured': 'Рекомендуемый пост',
            'allow_comments': 'Разрешить комментарии'
        }
        help_texts = {
            'excerpt': 'Максимум 300 символов. Используется в превью поста.',
            'tags': 'Разделяйте теги запятыми',
            'is_featured': 'Пост будет отображаться в разделе рекомендуемых'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только активные категории
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        
        # Делаем некоторые поля обязательными
        self.fields['title'].required = True
        self.fields['content'].required = True

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError('Заголовок должен содержать минимум 5 символов.')
        return title

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if tags:
            # Очищаем и форматируем теги
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if len(tag_list) > 10:
                raise forms.ValidationError('Максимум 10 тегов разрешено.')
            return ', '.join(tag_list)
        return tags


class CommentForm(forms.ModelForm):
    """Форма для добавления комментариев"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Поделитесь своими мыслями...',
                'required': True
            })
        }
        labels = {
            'content': 'Комментарий'
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content.strip()) < 10:
            raise forms.ValidationError('Комментарий должен содержать минимум 10 символов.')
        return content


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        }),
        label='Имя'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия'
        }),
        label='Фамилия'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        }),
        label='Email'
    )
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'location', 'website', 'github_url', 'linkedin_url']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о себе...',
                'maxlength': 500
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш город или страна'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/username'
            })
        }
        labels = {
            'bio': 'О себе',
            'avatar': 'Аватар',
            'location': 'Местоположение',
            'website': 'Веб-сайт',
            'github_url': 'GitHub',
            'linkedin_url': 'LinkedIn'
        }
        help_texts = {
            'bio': 'Максимум 500 символов',
            'avatar': 'Рекомендуемый размер: 300x300 пикселей'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if self.user:
            # Обновляем данные пользователя
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
            
            profile.user = self.user
        
        if commit:
            profile.save()
        
        return profile


class NewsletterForm(forms.ModelForm):
    """Форма для подписки на рассылку"""
    
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш email',
                'required': True
            })
        }
        labels = {
            'email': 'Email для подписки'
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Newsletter.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError('Этот email уже подписан на рассылку.')
        return email


class UserRegistrationForm(UserCreationForm):
    """Расширенная форма регистрации пользователей"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        }),
        label='Email'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        }),
        label='Имя'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия'
        }),
        label='Фамилия'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Выберите имя пользователя'
            })
        }
        labels = {
            'username': 'Имя пользователя'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(user=user)
        
        return user


class CategoryForm(forms.ModelForm):
    """Форма для создания и редактирования категорий"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название категории'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание категории...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#007bff'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-code (Font Awesome класс)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'color': 'Цвет',
            'icon': 'Иконка',
            'is_active': 'Активна'
        }
        help_texts = {
            'color': 'Цвет для отображения категории',
            'icon': 'CSS класс иконки Font Awesome (например: fas fa-code)'
        }


class SearchForm(forms.Form):
    """Форма для поиска постов"""
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по постам...'
        }),
        label='Поиск'
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Категория'
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-published_at', 'Сначала новые'),
            ('published_at', 'Сначала старые'),
            ('-views_count', 'По популярности'),
            ('-likes_count', 'По лайкам'),
            ('title', 'По алфавиту'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Сортировка'
    )


class AuthorRequestForm(forms.ModelForm):
    """Форма для подачи заявки на статус автора"""
    
    class Meta:
        model = AuthorRequest
        fields = ['motivation', 'experience', 'sample_topics']
        widgets = {
            'motivation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите, почему вы хотите стать автором на нашем сайте...'
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите ваш опыт в области, о которой планируете писать...'
            }),
            'sample_topics': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Какие темы вы планируете освещать? (например: Python, машинное обучение, веб-разработка...)'
            }),
        }
        labels = {
            'motivation': 'Мотивация *',
            'experience': 'Ваш опыт',
            'sample_topics': 'Планируемые темы статей',
        }
    
    def clean_motivation(self):
        motivation = self.cleaned_data['motivation']
        if len(motivation) < 50:
            raise forms.ValidationError('Мотивация должна содержать не менее 50 символов.')
        return motivation