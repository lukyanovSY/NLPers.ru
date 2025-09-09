from django import forms
from .models import ArchiveFile, FileCategory, FileComment, Playlist


class ArchiveFileForm(forms.ModelForm):
    """Форма для загрузки и редактирования файлов"""
    
    class Meta:
        model = ArchiveFile
        fields = [
            'title', 'description', 'file', 'thumbnail', 'category', 
            'file_type', 'tags', 'is_featured', 'allow_comments'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название файла...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание файла...'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: образование, видео, Python'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'file': 'Файл',
            'thumbnail': 'Превью (необязательно)',
            'category': 'Категория',
            'file_type': 'Тип файла',
            'tags': 'Теги',
            'is_featured': 'Рекомендуемый файл',
            'allow_comments': 'Разрешить комментарии'
        }
        help_texts = {
            'file': 'Максимальный размер файла: 100 MB',
            'thumbnail': 'Изображение для превью файла',
            'tags': 'Разделяйте теги запятыми'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только активные категории
        self.fields['category'].queryset = FileCategory.objects.filter(is_active=True)
        
    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            # Проверяем размер файла (100 MB)
            if file.size > 100 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 100 MB.')
        return file

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if tags:
            # Очищаем и форматируем теги
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if len(tag_list) > 15:
                raise forms.ValidationError('Максимум 15 тегов разрешено.')
            return ', '.join(tag_list)
        return tags


class FileCategoryForm(forms.ModelForm):
    """Форма для создания и редактирования категорий файлов"""
    
    class Meta:
        model = FileCategory
        fields = ['name', 'description', 'icon', 'color', 'is_active']
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
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-folder (Font Awesome класс)'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#28a745'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'icon': 'Иконка',
            'color': 'Цвет',
            'is_active': 'Активна'
        }
        help_texts = {
            'icon': 'CSS класс иконки Font Awesome (например: fas fa-folder)',
            'color': 'Цвет для отображения категории'
        }


class FileCommentForm(forms.ModelForm):
    """Форма для добавления комментариев к файлам"""
    
    class Meta:
        model = FileComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Поделитесь своим мнением о файле...',
                'required': True
            })
        }
        labels = {
            'content': 'Комментарий'
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content.strip()) < 5:
            raise forms.ValidationError('Комментарий должен содержать минимум 5 символов.')
        return content


class PlaylistForm(forms.ModelForm):
    """Форма для создания и редактирования плейлистов"""
    
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название плейлиста...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание плейлиста...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'is_public': 'Публичный плейлист'
        }
        help_texts = {
            'is_public': 'Другие пользователи смогут видеть этот плейлист'
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError('Название плейлиста должно содержать минимум 3 символа.')
        return name


class FileSearchForm(forms.Form):
    """Форма для поиска файлов"""
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск файлов...'
        }),
        label='Поиск'
    )
    
    file_type = forms.ChoiceField(
        choices=[('', 'Все типы')] + ArchiveFile.FILE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Тип файла'
    )
    
    category = forms.ModelChoiceField(
        queryset=FileCategory.objects.filter(is_active=True),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Категория'
    )
    
    is_public = forms.ChoiceField(
        choices=[
            ('', 'Все файлы'),
            ('True', 'Только публичные'),
            ('False', 'Только приватные')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Статус публикации'
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-uploaded_at', 'Сначала новые'),
            ('uploaded_at', 'Сначала старые'),
            ('-downloads_count', 'По популярности'),
            ('-likes_count', 'По лайкам'),
            ('title', 'По алфавиту'),
            ('-views_count', 'По просмотрам'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Сортировка'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем значения по умолчанию
        self.fields['sort_by'].initial = '-created_at'