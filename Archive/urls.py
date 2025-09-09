from django.urls import path
from . import views

app_name = 'Archive'

urlpatterns = [
    # Главная страница архива
    path('', views.ArchiveHomeView.as_view(), name='index'),
    
    # Просмотр файлов
    path('files/', views.FileListView.as_view(), name='file_list'),
    path('file/<int:pk>/', views.FileDetailView.as_view(), name='file_detail'),
    path('file/<int:pk>/download/', views.file_download, name='file_download'),
    
    # Категории файлов
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Управление файлами (для авторизованных пользователей)
    path('upload/', views.FileUploadView.as_view(), name='file_upload'),
    path('my-files/', views.UserFilesView.as_view(), name='user_files'),
    
    # Файлы по типам
    path('images/', views.images_list, name='images_list'),
    path('videos/', views.videos_list, name='videos_list'),
    path('audio/', views.audio_list, name='audio_list'),
    path('documents/', views.documents_list, name='documents_list'),
    
    # Комментарии
    path('file/<int:pk>/comment/', views.add_comment, name='add_comment'),
]