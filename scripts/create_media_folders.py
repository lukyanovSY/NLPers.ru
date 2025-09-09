#!/usr/bin/env python3
"""
Скрипт для создания структуры медиа папок
"""

import os
from pathlib import Path

def create_media_structure():
    """Создает структуру папок для медиа файлов"""
    
    # Базовые пути
    base_dir = Path(__file__).resolve().parent.parent
    media_root = base_dir / 'media'
    
    # Папки для создания
    folders = [
        'uploads',
        'images',
        'documents', 
        'videos',
        'audio',
        'images/thumbnails',
        'images/profiles',
        'documents/archives',
        'videos/previews',
        'audio/previews'
    ]
    
    print("Создание структуры медиа папок...")
    
    for folder in folders:
        folder_path = media_root / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Создана папка: {folder_path}")
        
        # Создаем .gitkeep файлы чтобы папки отслеживались git
        gitkeep_path = folder_path / '.gitkeep'
        if not gitkeep_path.exists():
            gitkeep_path.write_text("# This file ensures the folder is tracked by git\n")
    
    print("✓ Структура медиа папок создана успешно!")

if __name__ == "__main__":
    create_media_structure()