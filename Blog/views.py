from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.urls import reverse_lazy, reverse
import json

try:
    from .models import Post, Category, Comment, Like, Follow, Newsletter, UserProfile, AuthorRequest, Tag
    from .forms import PostForm, CommentForm, UserProfileForm, NewsletterForm, UserRegistrationForm, AuthorRequestForm
except:
    # Если модели не доступны, создаем пустые классы
    Post = Category = Comment = Like = Follow = Newsletter = UserProfile = AuthorRequest = Tag = None
    PostForm = CommentForm = UserProfileForm = NewsletterForm = UserRegistrationForm = AuthorRequestForm = None


class BlogHomeView(ListView):
    """Главная страница блога"""
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        if Post:
            return Post.objects.filter(status='published').select_related('author', 'category').order_by('-published_at')
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if Post and Category:
            context['featured_posts'] = Post.objects.filter(status='published', is_featured=True)[:3]
            context['categories'] = Category.objects.filter(is_active=True).annotate(total_posts=Count('posts'))
            context['latest_posts'] = Post.objects.filter(status='published')[:5]
        else:
            # Заглушки для случая, когда модели не работают
            context['featured_posts'] = []
            context['categories'] = []
            context['latest_posts'] = []
            
        return context


class PostListView(ListView):
    """Список всех постов"""
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        if not Post:
            return []
            
        queryset = Post.objects.filter(status='published').select_related('author', 'category')
        
        # Поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Фильтр по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Сортировка
        sort_by = self.request.GET.get('sort', '-published_at')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Category:
            context['categories'] = Category.objects.filter(is_active=True).annotate(total_posts=Count('posts'))
        else:
            context['categories'] = []
        return context


class PostDetailView(DetailView):
    """Детальная страница поста"""
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        if Post:
            return Post.objects.filter(status='published').select_related('author', 'category')
        return []
    
    def get_object(self):
        if not Post:
            from django.http import Http404
            raise Http404("Post model not available")
            
        post = super().get_object()
        # Увеличиваем счетчик просмотров
        post.views_count += 1
        post.save(update_fields=['views_count'])
        return post
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not Post:
            return context
            
        post = self.object
        
        # Комментарии
        if Comment:
            context['comments'] = post.comments.filter(is_approved=True, parent=None).select_related('author')
        else:
            context['comments'] = []
        
        # Теги
        context['tags'] = post.get_tags_list() if hasattr(post, 'get_tags_list') else []
        
        # Похожие посты
        if post.category:
            context['related_posts'] = Post.objects.filter(
                category=post.category, 
                status='published'
            ).exclude(id=post.id)[:4]
        
        # Навигация между постами
        context['previous_post'] = Post.objects.filter(
            status='published',
            published_at__lt=post.published_at
        ).first()
        
        context['next_post'] = Post.objects.filter(
            status='published', 
            published_at__gt=post.published_at
        ).last()
        
        if self.request.user.is_authenticated and Like:
            # Проверяем, лайкнул ли пользователь пост
            context['user_liked'] = Like.objects.filter(
                user=self.request.user,
                content_type='post',
                object_id=post.id
            ).exists()
            
            # Проверяем, подписан ли на автора
            if Follow:
                context['user_following_author'] = Follow.objects.filter(
                    follower=self.request.user,
                    following_user=post.author
                ).exists()
        
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def get(self, request, *args, **kwargs):
        if not Post or not PostForm:
            messages.error(request, 'Создание постов временно недоступно.')
            return redirect('Blog:index')
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('Blog:post_detail', kwargs={'slug': self.object.slug})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование поста"""
    template_name = 'blog/post_form.html'
    
    def get_form_class(self):
        return PostForm if PostForm else None
    
    def get_queryset(self):
        if Post:
            return Post.objects.filter(author=self.request.user)
        return []
    
    def get_success_url(self):
        return reverse('Blog:post_detail', kwargs={'slug': self.object.slug})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление поста"""
    success_url = reverse_lazy('Blog:index')
    
    def get_queryset(self):
        if Post:
            return Post.objects.filter(author=self.request.user)
        return []


class CategoryListView(ListView):
    """Список всех категорий"""
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        if Category:
            return Category.objects.filter(is_active=True).annotate(
                total_posts=Count('posts', filter=Q(posts__status='published'))
            ).order_by('name')
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if Post:
            # Получаем общую статистику
            context['total_posts'] = Post.objects.filter(status='published').count()
            context['total_categories'] = Category.objects.filter(is_active=True).count()
            
            # Поиск категорий
            search_query = self.request.GET.get('search')
            if search_query:
                context['search_query'] = search_query
        else:
            context['total_posts'] = 0
            context['total_categories'] = 0
            
        return context


class CategoryDetailView(DetailView):
    """Посты в категории"""
    template_name = 'blog/category_detail.html'
    context_object_name = 'category'
    
    def get_queryset(self):
        return Category.objects.all() if Category else []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not Category or not Post:
            context['posts'] = []
            context['other_categories'] = []
            context['recent_posts'] = []
            return context
            
        category = self.object
        posts = Post.objects.filter(category=category, status='published').order_by('-published_at')
        
        paginator = Paginator(posts, 10)
        page = self.request.GET.get('page')
        context['posts'] = paginator.get_page(page)
        
        # Другие категории с количеством постов
        context['other_categories'] = Category.objects.filter(is_active=True).annotate(
            total_posts=Count('posts', filter=Q(posts__status='published'))
        ).order_by('name')
        
        # Последние популярные посты из других категорий
        context['recent_posts'] = Post.objects.filter(
            status='published'
        ).exclude(category=category).order_by('-views_count')[:5]
        
        # Проверяем подписку на категорию для авторизованного пользователя
        if self.request.user.is_authenticated and Follow:
            context['user_following_category'] = Follow.objects.filter(
                follower=self.request.user,
                following_category=category
            ).exists()
        
        return context


class UserProfileView(DetailView):
    """Профиль пользователя"""
    model = User
    template_name = 'blog/user_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        # Посты пользователя
        if Post:
            posts = Post.objects.filter(author=user, status='published').order_by('-published_at')
            paginator = Paginator(posts, 10)
            page = self.request.GET.get('page')
            context['posts'] = paginator.get_page(page)
            context['posts_count'] = posts.count()
        else:
            context['posts'] = []
            context['posts_count'] = 0
        
        # Статистика
        if Follow:
            context['followers_count'] = Follow.objects.filter(following_user=user).count()
            context['following_count'] = Follow.objects.filter(follower=user).count()
        else:
            context['followers_count'] = 0
            context['following_count'] = 0
        
        if self.request.user.is_authenticated and self.request.user != user and Follow:
            context['is_following'] = Follow.objects.filter(
                follower=self.request.user,
                following_user=user
            ).exists()
        
        return context


class TagListView(ListView):
    """Список всех тегов"""
    template_name = 'blog/tag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        if Tag:
            return Tag.objects.filter(is_active=True).annotate(
                total_posts=Count('posts', filter=Q(posts__status='published'))
            ).order_by('name')
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if Post:
            # Получаем общую статистику
            context['total_posts'] = Post.objects.filter(status='published').count()
            context['total_tags'] = Tag.objects.filter(is_active=True).count()
            
            # Поиск тегов
            search_query = self.request.GET.get('search')
            if search_query:
                context['search_query'] = search_query
        else:
            context['total_posts'] = 0
            context['total_tags'] = 0
            
        return context


class TagDetailView(DetailView):
    """Посты по тегу"""
    template_name = 'blog/tag_detail.html'
    context_object_name = 'tag'
    
    def get_queryset(self):
        if Tag:
            return Tag.objects.filter(is_active=True)
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.object:
            # Получаем посты с этим тегом
            posts = []
            total_posts = 0
            if Post:
                posts = Post.objects.filter(
                    tag_objects=self.object,
                    status='published'
                ).select_related('author', 'category').order_by('-published_at')
                total_posts = posts.count()
            
            # Получаем файлы с этим тегом
            archive_files = []
            total_files = 0
            try:
                from Archive.models import ArchiveFile
                archive_files = ArchiveFile.objects.filter(
                    tag_objects=self.object,
                    is_public=True
                ).select_related('uploaded_by', 'category').order_by('-uploaded_at')
                total_files = archive_files.count()
            except ImportError:
                pass
            
            # Объединяем контент
            all_content = []
            
            # Добавляем посты
            for post in posts:
                all_content.append({
                    'type': 'post',
                    'object': post,
                    'title': post.title,
                    'date': post.published_at or post.created_at,
                    'author': post.author,
                    'category': post.category,
                    'views': post.views_count,
                    'likes': post.likes_count,
                    'comments': post.comments_count,
                    'url': post.get_absolute_url(),
                    'excerpt': post.excerpt,
                    'image': post.featured_image
                })
            
            # Добавляем файлы
            for file in archive_files:
                all_content.append({
                    'type': 'file',
                    'object': file,
                    'title': file.title,
                    'date': file.uploaded_at,
                    'author': file.uploaded_by,
                    'category': file.category,
                    'views': file.views_count,
                    'likes': file.likes_count,
                    'downloads': file.downloads_count,
                    'url': file.get_absolute_url(),
                    'excerpt': file.description,
                    'file_type': file.file_type,
                    'file_size': file.file_size
                })
            
            # Сортируем по дате
            all_content.sort(key=lambda x: x['date'], reverse=True)
            
            # Поиск
            search_query = self.request.GET.get('search')
            if search_query:
                filtered_content = []
                for item in all_content:
                    if (search_query.lower() in item['title'].lower() or 
                        (item['excerpt'] and search_query.lower() in item['excerpt'].lower())):
                        filtered_content.append(item)
                all_content = filtered_content
                context['search_query'] = search_query
            
            # Пагинация
            paginator = Paginator(all_content, 12)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['content'] = page_obj
            context['total_posts'] = total_posts
            context['total_files'] = total_files
            context['total_content'] = total_posts + total_files
        else:
            context['content'] = []
            context['total_posts'] = 0
            context['total_files'] = 0
            context['total_content'] = 0
            
        return context


class TaggedPostsView(ListView):
    """Посты по тегу (для обратной совместимости)"""
    template_name = 'blog/tagged_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        if not Post:
            return []
            
        tag = self.kwargs['tag']
        return Post.objects.filter(
            tags__icontains=tag,
            status='published'
        ).order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.kwargs['tag']
        return context


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя"""
    if not UserProfile or not UserProfileForm:
        messages.error(request, 'Редактирование профиля временно недоступно.')
        return redirect('Blog:index')
        
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('Blog:user_profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    return render(request, 'blog/edit_profile.html', {'form': form})


@login_required
def toggle_like(request):
    """AJAX лайк/дизлайк"""
    if not Post or not Like:
        return JsonResponse({'error': 'Likes not available'}, status=400)
        
    if request.method == 'POST':
        data = json.loads(request.body)
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        
        if content_type == 'post':
            try:
                post = Post.objects.get(id=object_id)
                like, created = Like.objects.get_or_create(
                    user=request.user,
                    content_type='post',
                    object_id=object_id,
                    defaults={'post': post}
                )
                
                if not created:
                    like.delete()
                    liked = False
                    post.likes_count = max(0, post.likes_count - 1)
                else:
                    liked = True
                    post.likes_count += 1
                
                post.save(update_fields=['likes_count'])
                
                return JsonResponse({
                    'liked': liked,
                    'likes_count': post.likes_count
                })
            except Post.DoesNotExist:
                return JsonResponse({'error': 'Post not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def toggle_follow(request):
    """AJAX подписка/отписка"""
    if not Follow:
        return JsonResponse({'error': 'Follow not available'}, status=400)
        
    if request.method == 'POST':
        data = json.loads(request.body)
        follow_type = data.get('follow_type')
        object_id = data.get('object_id')
        
        if follow_type == 'user':
            try:
                user_to_follow = User.objects.get(id=object_id)
                follow, created = Follow.objects.get_or_create(
                    follower=request.user,
                    following_user=user_to_follow,
                    defaults={'follow_type': 'user'}
                )
                
                if not created:
                    follow.delete()
                    followed = False
                else:
                    followed = True
                
                return JsonResponse({'followed': followed})
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
                
        elif follow_type == 'category':
            if not Category:
                return JsonResponse({'error': 'Category not available'}, status=400)
            try:
                category_to_follow = Category.objects.get(id=object_id)
                follow, created = Follow.objects.get_or_create(
                    follower=request.user,
                    following_category=category_to_follow,
                    defaults={'follow_type': 'category'}
                )
                
                if not created:
                    follow.delete()
                    followed = False
                else:
                    followed = True
                
                return JsonResponse({'followed': followed})
            except Category.DoesNotExist:
                return JsonResponse({'error': 'Category not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_comment(request):
    """AJAX добавление комментария"""
    if not Post or not Comment:
        return JsonResponse({'error': 'Comments not available'}, status=400)
        
    if request.method == 'POST':
        post_slug = request.POST.get('post_slug')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        try:
            post = Post.objects.get(slug=post_slug)
            
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            
            # Обновляем счетчик комментариев
            post.comments_count = post.comments.filter(is_approved=True).count()
            post.save(update_fields=['comments_count'])
            
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'author': comment.author.get_full_name() or comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M')
            })
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def newsletter_subscribe(request):
    """Подписка на рассылку"""
    if not Newsletter or not NewsletterForm:
        messages.error(request, 'Подписка на рассылку временно недоступна.')
        return redirect('Blog:index')
        
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Спасибо за подписку на нашу рассылку!')
        else:
            messages.error(request, 'Ошибка при подписке. Проверьте введенные данные.')
    
    return redirect('Blog:index')


# ===============================
# ПРЕДСТАВЛЕНИЯ АУТЕНТИФИКАЦИИ
# ===============================

class CustomLoginView(LoginView):
    """Пользовательское представление входа"""
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return self.get_redirect_url() or '/'
    
    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Пользовательское представление выхода"""
    next_page = '/'
    template_name = 'auth/logout_confirm.html'
    http_method_names = ['get', 'post']
    
    def get(self, request, *args, **kwargs):
        """Показываем страницу подтверждения выхода"""
        if not request.user.is_authenticated:
            return redirect('/')
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        """Выполняем logout"""
        if request.user.is_authenticated:
            messages.success(request, f'До свидания, {request.user.username}! Вы успешно вышли из системы.')
        return super().post(request, *args, **kwargs)


def register_view(request):
    """Представление регистрации"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} успешно создан! Теперь вы можете войти в систему.')
            
            # Автоматический вход после регистрации
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})


@login_required
def user_dashboard(request):
    """Панель пользователя"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:5]
    
    # Проверяем статус заявки на авторство
    author_request = None
    try:
        author_request = AuthorRequest.objects.get(user=request.user)
    except AuthorRequest.DoesNotExist:
        pass
    
    # Проверяем, является ли пользователь автором
    is_author = request.user.groups.filter(name='Authors').exists()
    
    # Получаем загруженные файлы пользователя (если есть приложение Archive)
    user_files = []
    try:
        from Archive.models import ArchiveFile
        user_files = ArchiveFile.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')[:5]
    except ImportError:
        pass
    
    context = {
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_files': user_files,
        'posts_count': user_posts.count(),
        'files_count': len(user_files),
        'author_request': author_request,
        'is_author': is_author,
    }
    
    return render(request, 'auth/dashboard.html', context)


@login_required
def author_request_view(request):
    """Подача заявки на статус автора"""
    # Проверяем, есть ли уже заявка
    try:
        existing_request = AuthorRequest.objects.get(user=request.user)
        if existing_request.status == 'pending':
            messages.info(request, 'Ваша заявка уже подана и находится на рассмотрении.')
            return redirect('Blog:dashboard')
        elif existing_request.status == 'approved':
            messages.info(request, 'Вы уже являетесь автором!')
            return redirect('Blog:dashboard')
    except AuthorRequest.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = AuthorRequestForm(request.POST)
        if form.is_valid():
            author_request = form.save(commit=False)
            author_request.user = request.user
            author_request.save()
            messages.success(request, 'Ваша заявка на статус автора отправлена! Мы рассмотрим её в ближайшее время.')
            return redirect('Blog:dashboard')
    else:
        form = AuthorRequestForm()
    
    return render(request, 'auth/author_request.html', {'form': form})