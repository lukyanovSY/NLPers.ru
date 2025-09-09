from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.urls import reverse_lazy

# Безопасный импорт моделей
try:
    from .models import ArchiveFile, FileCategory, FileComment, FileLike, Playlist, Download
    from .forms import ArchiveFileForm
except ImportError:
    ArchiveFile = None
    FileCategory = None
    FileComment = None
    FileLike = None
    Playlist = None
    Download = None
    ArchiveFileForm = None


class ArchiveHomeView(TemplateView):
    """Главная страница архива"""
    template_name = 'archive/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if ArchiveFile and FileCategory:
            # Последние файлы (только с существующими файлами)
            context['recent_files'] = ArchiveFile.objects.filter(
                is_public=True
            ).exclude(file='').order_by('-uploaded_at')[:6]
            # Категории
            context['categories'] = FileCategory.objects.filter(is_active=True).order_by('name')
            # Статистика (только файлы с существующими файлами)
            context['total_files'] = ArchiveFile.objects.filter(
                is_public=True
            ).exclude(file='').count()
            # Общее количество скачиваний
            context['total_downloads'] = sum(
                file.downloads_count for file in ArchiveFile.objects.filter(is_public=True).exclude(file='')
            )
        else:
            context['recent_files'] = []
            context['categories'] = []
            context['total_files'] = 0
            context['total_downloads'] = 0
            
        return context


class FileListView(ListView):
    """Список файлов"""
    template_name = 'archive/file_list.html'
    context_object_name = 'files'
    paginate_by = 20
    
    def get_queryset(self):
        if ArchiveFile:
            return ArchiveFile.objects.filter(is_public=True).exclude(file='').order_by('-uploaded_at')
        return []
    
    def get_context_data(self, **kwargs):
        """Добавляем дополнительный контекст"""
        context = super().get_context_data(**kwargs)
        context['recent_files'] = ArchiveFile.objects.filter(
            is_public=True
        ).exclude(file='').order_by('-uploaded_at')[:6]
        return context



class FileDetailView(DetailView):
    """Детальная страница файла"""
    template_name = 'archive/file_detail.html'
    context_object_name = 'file'
    
    def get_queryset(self):
        if ArchiveFile:
            return ArchiveFile.objects.filter(is_public=True).exclude(file='')
        return []
    
    def get_object(self, queryset=None):
        """Увеличиваем счетчик просмотров при просмотре файла"""
        obj = super().get_object(queryset)
        if obj:
            obj.views_count += 1
            obj.save()
        return obj


class CategoryDetailView(DetailView):
    """Файлы в категории"""
    template_name = 'archive/category_detail.html'
    context_object_name = 'category'
    
    def get_queryset(self):
        if FileCategory:
            return FileCategory.objects.filter(is_active=True)
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if ArchiveFile and self.object:
            files = ArchiveFile.objects.filter(
                category=self.object,
                is_public=True
            ).exclude(file='').select_related('uploaded_by').order_by('-uploaded_at')
            
            paginator = Paginator(files, 12)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['files'] = page_obj
            context['total_files'] = files.count()
        else:
            context['files'] = []
            context['total_files'] = 0
            
        return context


def file_download(request, pk):
    """Скачивание файла"""
    if not ArchiveFile:
        raise Http404("Архив недоступен")
    
    file_obj = get_object_or_404(ArchiveFile, pk=pk, is_public=True)
    
    # Проверяем, что файл существует
    if not file_obj.file:
        messages.error(request, 'Файл не найден')
        return redirect('Archive:index')
    
    # Увеличиваем счетчик скачиваний
    file_obj.downloads_count += 1
    file_obj.save()
    
    messages.info(request, f'Скачивание файла: {file_obj.title}')
    return redirect('Archive:index')


class FileUploadView(LoginRequiredMixin, CreateView):
    """Загрузка файла"""
    template_name = 'archive/file_upload.html'
    form_class = ArchiveFileForm
    success_url = reverse_lazy('Archive:index')
    
    def dispatch(self, request, *args, **kwargs):
        """Проверяем права доступа"""
        if not request.user.is_authenticated:
            messages.error(request, 'Для загрузки файлов необходимо войти в систему.')
            return redirect('Blog:login')
        
        # Проверяем, является ли пользователь автором
        if not request.user.groups.filter(name='Authors').exists():
            messages.error(request, 'Для загрузки файлов необходимо иметь статус автора.')
            return redirect('Blog:dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Сохраняем файл с привязкой к пользователю"""
        file_obj = form.save(commit=False)
        file_obj.uploaded_by = self.request.user
        
        # Устанавливаем статус публикации в зависимости от прав пользователя
        if self.request.user.is_staff:
            file_obj.is_public = True
        else:
            file_obj.is_public = False  # Требует модерации
        
        file_obj.save()
        form.save_m2m()  # Сохраняем связи many-to-many (теги)
        
        if file_obj.is_public:
            messages.success(self.request, f'Файл "{file_obj.title}" успешно загружен и опубликован!')
        else:
            messages.success(self.request, f'Файл "{file_obj.title}" загружен и отправлен на модерацию.')
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Обработка ошибок формы"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Добавляем дополнительный контекст"""
        context = super().get_context_data(**kwargs)
        context['categories'] = FileCategory.objects.filter(is_active=True) if FileCategory else []
        return context


def images_list(request):
    """Список изображений"""
    context = {'files': []}
    return render(request, 'archive/images_list.html', context)


def videos_list(request):
    """Список видео"""
    context = {'files': []}
    return render(request, 'archive/videos_list.html', context)


def audio_list(request):
    """Список аудио"""
    context = {'files': []}
    return render(request, 'archive/audio_list.html', context)


def documents_list(request):
    """Список документов"""
    context = {'files': []}
    return render(request, 'archive/documents_list.html', context)


@login_required
def add_comment(request, pk):
    """Добавление комментария к файлу"""
    if not ArchiveFile or not FileComment:
        messages.error(request, 'Функция комментариев недоступна')
        return redirect('Archive:index')
    
    file_obj = get_object_or_404(ArchiveFile, pk=pk, is_public=True)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, 'Комментарий не может быть пустым')
            return redirect('Archive:file_detail', pk=pk)
        
        # Создаем комментарий
        comment = FileComment.objects.create(
            file=file_obj,
            author=request.user,
            content=content
        )
        
        messages.success(request, 'Комментарий успешно добавлен!')
        return redirect('Archive:file_detail', pk=pk)
    
    return redirect('Archive:file_detail', pk=pk)


class UserFilesView(LoginRequiredMixin, ListView):
    """Файлы пользователя"""
    template_name = 'archive/user_files.html'
    context_object_name = 'files'
    paginate_by = 12
    
    def get_queryset(self):
        if ArchiveFile:
            return ArchiveFile.objects.filter(
                uploaded_by=self.request.user
            ).select_related('category').order_by('-uploaded_at')
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['total_files'] = self.get_queryset().count()
        context['public_files'] = self.get_queryset().filter(is_public=True).count()
        context['pending_files'] = self.get_queryset().filter(is_public=False).count()
        return context
