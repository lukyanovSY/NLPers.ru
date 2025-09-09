from django.shortcuts import render
from django.views.generic import *
from .models import *
from Blog.models import Category, Post
from Archive.models import ArchiveFile

def home(request):
    # Получаем все категории для отображения на главной странице
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    # Получаем последние опубликованные статьи (максимум 8 для отображения в карусели)
    latest_posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category').prefetch_related('author__userprofile').order_by('-published_at', '-created_at')[:8]
    
    # Получаем последние файлы изображений (максимум 4 для отображения в секции sell-nfts-area)
    latest_images = ArchiveFile.objects.filter(
        file_type='image',
        is_public=True
    ).select_related('uploaded_by', 'category').prefetch_related('uploaded_by__userprofile').order_by('-uploaded_at')[:4]
    
    context = {
        'categories': categories,
        'latest_posts': latest_posts,
        'latest_images': latest_images,
    }
    
    return render(request, 'home/index.html', context)
    #return render(request, 'abc/activity.html', )