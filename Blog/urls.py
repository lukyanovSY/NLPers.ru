from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'Blog'

urlpatterns = [
    # Главная страница блога
    path('', views.BlogHomeView.as_view(), name='index'),
    
    # Редирект для совместимости
    path('index.html', RedirectView.as_view(url='/blog/', permanent=True)),
    
    # Посты
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Категории
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Теги
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    path('tag/<str:tag>/', views.TaggedPostsView.as_view(), name='tagged_posts'),
    
    # Профили пользователей
    path('user/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # AJAX действия
    path('ajax/like/', views.toggle_like, name='toggle_like'),
    path('ajax/follow/', views.toggle_follow, name='toggle_follow'),
    path('ajax/comment/', views.add_comment, name='add_comment'),
    
    # Подписка на рассылку
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Аутентификация
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('author-request/', views.author_request_view, name='author_request'),
]