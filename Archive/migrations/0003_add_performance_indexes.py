"""
Добавляет индексы для оптимизации производительности
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Archive', '0002_archivefile_thumbnail'),
    ]

    operations = [
        # Индексы для модели ArchiveFile
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_archivefile_is_public_uploaded ON archive_archivefile (is_public, uploaded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_archivefile_is_public_uploaded;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_archivefile_category_is_public ON archive_archivefile (category_id, is_public);",
            reverse_sql="DROP INDEX IF EXISTS idx_archivefile_category_is_public;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_archivefile_file_type ON archive_archivefile (file_type, is_public);",
            reverse_sql="DROP INDEX IF EXISTS idx_archivefile_file_type;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_archivefile_downloads_count ON archive_archivefile (downloads_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_archivefile_downloads_count;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_archivefile_views_count ON archive_archivefile (views_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_archivefile_views_count;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_archivefile_is_featured ON archive_archivefile (is_featured, uploaded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_archivefile_is_featured;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_archivefile_uploaded_by ON archive_archivefile (uploaded_by_id, uploaded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_archivefile_uploaded_by;"
        ),
        
        # Индексы для модели FileCategory
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_filecategory_is_active ON archive_filecategory (is_active, name);",
            reverse_sql="DROP INDEX IF EXISTS idx_filecategory_is_active;"
        ),
        
        # Индексы для модели FileComment
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_filecomment_file_approved ON archive_filecomment (file_id, is_approved, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_filecomment_file_approved;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_filecomment_author_created ON archive_filecomment (author_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_filecomment_author_created;"
        ),
        
        # Индексы для модели FileLike
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_filelike_file ON archive_filelike (file_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_filelike_file;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_filelike_user_created ON archive_filelike (user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_filelike_user_created;"
        ),
        
        # Индексы для модели Download
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_download_file_created ON archive_download (file_id, downloaded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_download_file_created;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_download_user_created ON archive_download (user_id, downloaded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_download_user_created;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_download_ip_created ON archive_download (ip_address, downloaded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_download_ip_created;"
        ),
        
        # Индексы для модели Playlist
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_playlist_created_by ON archive_playlist (created_by_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_playlist_created_by;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_playlist_is_public ON archive_playlist (is_public, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_playlist_is_public;"
        ),
    ]
