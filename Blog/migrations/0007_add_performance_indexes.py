"""
Добавляет индексы для оптимизации производительности
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0006_tag_post_tag_objects'),
    ]

    operations = [
        # Индексы для модели Post
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_post_status_published_at ON blog_post (status, published_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_post_status_published_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_post_category_status ON blog_post (category_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_post_category_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_post_author_status ON blog_post (author_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_post_author_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_post_views_count ON blog_post (views_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_post_views_count;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_post_likes_count ON blog_post (likes_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_post_likes_count;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_post_is_featured ON blog_post (is_featured, published_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_post_is_featured;"
        ),
        
        # Индексы для модели Comment
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_comment_post_approved ON blog_comment (post_id, is_approved, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_comment_post_approved;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_comment_author_created ON blog_comment (author_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_comment_author_created;"
        ),
        
        # Индексы для модели Like
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_like_content_object ON blog_like (content_type, object_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_like_content_object;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_like_user_created ON blog_like (user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_like_user_created;"
        ),
        
        # Индексы для модели Follow
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_follow_follower_type ON blog_follow (follower_id, follow_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_follow_follower_type;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_follow_created ON blog_follow (created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_follow_created;"
        ),
        
        # Индексы для модели Category
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_category_is_active ON blog_category (is_active, name);",
            reverse_sql="DROP INDEX IF EXISTS idx_category_is_active;"
        ),
        
        # Индексы для модели Tag
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_tag_is_active ON blog_tag (is_active, name);",
            reverse_sql="DROP INDEX IF EXISTS idx_tag_is_active;"
        ),
        
        # Индексы для модели UserProfile
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_userprofile_is_verified ON blog_userprofile (is_verified);",
            reverse_sql="DROP INDEX IF EXISTS idx_userprofile_is_verified;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_userprofile_posts_count ON blog_userprofile (posts_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_userprofile_posts_count;"
        ),
        
        # Индексы для модели AuthorRequest
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_authorrequest_status ON blog_authorrequest (status, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_authorrequest_status;"
        ),
    ]
