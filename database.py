import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'portfolio.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            full_description TEXT NOT NULL,
            preview_image TEXT,
            live_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Auth sessions table for Telegram authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT UNIQUE NOT NULL,
            telegram_user_id INTEGER,
            username TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            approved_at TIMESTAMP
        )
    ''')

    # Admin users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tags table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Project tags relationship table (many-to-many)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_tags (
            project_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (project_id, tag_id),
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_sample_data():
    """Insert sample projects if database is empty"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if projects exist
    cursor.execute('SELECT COUNT(*) FROM projects')
    count = cursor.fetchone()[0]

    if count == 0:
        sample_projects = [
            {
                'title': 'E-commerce Website',
                'description': 'Современный интернет-магазин с адаптивным дизайном',
                'full_description': 'Полнофункциональный интернет-магазин, разработанный с использованием Flask и современного frontend стека. Включает корзину покупок, систему оплаты, админ-панель для управления товарами.',
                'preview_image': '/static/images/project1-preview.jpg',
                'live_url': 'https://example-shop.com'
            },
            {
                'title': 'Blog Platform',
                'description': 'Платформа для блогинга с системой комментариев',
                'full_description': 'Современная блог-платформа с редактором Markdown, системой тегов, комментариями и авторизацией пользователей. Адаптивный дизайн и SEO-оптимизация.',
                'preview_image': '/static/images/project2-preview.jpg',
                'live_url': 'https://example-blog.com'
            },
            {
                'title': 'Portfolio Dashboard',
                'description': 'Интерактивная админ-панель для управления контентом',
                'full_description': 'Профессиональная админ-панель с графиками, аналитикой, управлением пользователями и контентом. Реализована с использованием Chart.js и современных UI компонентов.',
                'preview_image': '/static/images/project3-preview.jpg',
                'live_url': 'https://example-dashboard.com'
            }
        ]

        for project in sample_projects:
            cursor.execute('''
                INSERT INTO projects (title, description, full_description, preview_image, live_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project['title'],
                project['description'],
                project['full_description'],
                project['preview_image'],
                project['live_url']
            ))

    conn.commit()
    conn.close()

def get_all_projects():
    """Get all projects from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
    projects = cursor.fetchall()
    conn.close()
    return [dict(project) for project in projects]

def get_project_by_id(project_id):
    """Get project by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    conn.close()
    return dict(project) if project else None

def add_project(title, description, full_description, preview_image, live_url):
    """Add new project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (title, description, full_description, preview_image, live_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, description, full_description, preview_image, live_url))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def update_project(project_id, title, description, full_description, preview_image, live_url):
    """Update existing project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects
        SET title = ?, description = ?, full_description = ?,
            preview_image = ?, live_url = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (title, description, full_description, preview_image, live_url, project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    """Delete project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

# Auth functions
def create_auth_session(session_token, telegram_user_id, username):
    """Create new auth session"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Set expiration time (1 hour from now)
    cursor.execute('''
        INSERT INTO auth_sessions (session_token, telegram_user_id, username, expires_at)
        VALUES (?, ?, ?, datetime('now', '+1 hour'))
    ''', (session_token, telegram_user_id, username))

    conn.commit()
    conn.close()

def get_auth_session(session_token):
    """Get auth session by token"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM auth_sessions
        WHERE session_token = ? AND expires_at > datetime('now')
    ''', (session_token,))
    session = cursor.fetchone()
    conn.close()
    return dict(session) if session else None

def approve_auth_session(session_token):
    """Approve auth session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE auth_sessions
        SET status = 'approved', approved_at = CURRENT_TIMESTAMP
        WHERE session_token = ?
    ''', (session_token,))
    conn.commit()
    conn.close()

def reject_auth_session(session_token):
    """Reject auth session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE auth_sessions
        SET status = 'rejected', approved_at = CURRENT_TIMESTAMP
        WHERE session_token = ?
    ''', (session_token,))
    conn.commit()
    conn.close()

def is_admin_user(telegram_user_id):
    """Check if user is admin"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM admin_users
        WHERE telegram_user_id = ? AND is_active = 1
    ''', (telegram_user_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def add_admin_user(telegram_user_id, username):
    """Add admin user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO admin_users (telegram_user_id, username)
        VALUES (?, ?)
    ''', (telegram_user_id, username))
    conn.commit()
    conn.close()

# Tag functions
def get_all_tags():
    """Get all tags"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tags ORDER BY name')
    tags = cursor.fetchall()
    conn.close()
    return [dict(tag) for tag in tags]

def add_tag(name):
    """Add new tag"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO tags (name) VALUES (?)', (name,))
        tag_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tag_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def delete_tag(tag_id):
    """Delete tag"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
    conn.commit()
    conn.close()

def get_project_tags(project_id):
    """Get tags for specific project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.* FROM tags t
        INNER JOIN project_tags pt ON t.id = pt.tag_id
        WHERE pt.project_id = ?
        ORDER BY t.name
    ''', (project_id,))
    tags = cursor.fetchall()
    conn.close()
    return [dict(tag) for tag in tags]

def set_project_tags(project_id, tag_ids):
    """Set tags for project (replaces existing tags)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Remove existing tags
    cursor.execute('DELETE FROM project_tags WHERE project_id = ?', (project_id,))

    # Add new tags
    for tag_id in tag_ids:
        cursor.execute('INSERT INTO project_tags (project_id, tag_id) VALUES (?, ?)',
                      (project_id, tag_id))

    conn.commit()
    conn.close()

def get_projects_by_tag(tag_id):
    """Get all projects with specific tag"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.* FROM projects p
        INNER JOIN project_tags pt ON p.id = pt.project_id
        WHERE pt.tag_id = ?
        ORDER BY p.created_at DESC
    ''', (tag_id,))
    projects = cursor.fetchall()
    conn.close()
    return [dict(project) for project in projects]

if __name__ == '__main__':
    init_db()
    insert_sample_data()
    print("Database initialized successfully!")