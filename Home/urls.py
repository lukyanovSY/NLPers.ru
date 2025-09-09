from django.contrib import admin
from django.urls import path
from .views import *

app_name = 'Home'

urlpatterns = [
    path('', home, name='home'),
    #path('', PostListView.as_view(), name='blog'),
    #path('blog/', PostListView.as_view(), name='blog'),
    #path('post/create/', PostCreateView.as_view(), name='post_create'),
    #path('post/<str:slug>/', post_detail, name='post_detail'),
    #path('post/<str:slug>/update/', PostUpdateView.as_view(), name='post_update'),
    #path('post/<str:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),
    #path('category/<str:slug>/', PostByCategoryListView.as_view(), name="post_list_by_category"),
    #path('post/tags/<str:tag>/', PostByTagListView.as_view(), name='post_by_tags'),
    #path('author/<str:slug>/', AutorPostListView.as_view(), name='autor'),
    #path('post/author/<str:author>/', PostByAutorListView.as_view(), name='post_by_author'),
    
]
