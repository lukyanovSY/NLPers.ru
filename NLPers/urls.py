from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView

# Импортируем настройки админки
from . import admin as admin_config

urlpatterns = [
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('admin/', admin.site.urls),
    path('blog/', include('Blog.urls', namespace='Blog')),
    path('archive/', include('Archive.urls', namespace='Archive')),
    path('', include('Home.urls', namespace='Home')),
    
    # Redirects for compatibility with old URLs
    path('blog.html', RedirectView.as_view(url='/blog/', permanent=True)),
    path('blog-details.html', RedirectView.as_view(url='/blog/', permanent=True)),
    path('index.html', RedirectView.as_view(url='/', permanent=True)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
