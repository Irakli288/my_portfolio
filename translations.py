"""
Translation system for portfolio website
"""

TRANSLATIONS = {
    'name': 'Иракли Кекелашвили',
    'title': 'Fullstack Developer',
    'description': 'Иракли Кекелашвили создает современные веб-приложения, лендинги, веб-сервисы, телеграм боты и другие цифровые решения. Специализируется на разработке полнофункциональных решений от концепции до реализации.',
    'email': 'Email',
    'phone': 'Телефон',
    'telegram': 'Telegram',
    'github': 'GitHub',
    'my_works': 'Работы',
    'view_details': 'Подробнее',
    'view_project': 'Посмотреть проект',
    'projects': {
        1: {
            'title': 'E-commerce Website',
            'description': 'Современный интернет-магазин с адаптивным дизайном',
            'full_description': 'Полнофункциональный интернет-магазин, разработанный с использованием Flask и современного frontend стека. Включает корзину покупок, систему оплаты, админ-панель для управления товарами.'
        },
        2: {
            'title': 'Blog Platform',
            'description': 'Платформа для блогинга с системой комментариев',
            'full_description': 'Современная блог-платформа с редактором Markdown, системой тегов, комментариями и авторизацией пользователей. Адаптивный дизайн и SEO-оптимизация.'
        },
        3: {
            'title': 'Portfolio Dashboard',
            'description': 'Интерактивная админ-панель для управления контентом',
            'full_description': 'Профессиональная админ-панель с графиками, аналитикой, управлением пользователями и контентом. Реализована с использованием Chart.js и современных UI компонентов.'
        }
    }
}

def get_user_language(request):
    """
    Always return Russian language
    """
    return 'ru'

def get_translations(lang='ru'):
    """
    Get translations (always Russian)
    """
    return TRANSLATIONS

def get_country_from_ip(ip_address):
    """
    Always return RU (not used anymore)
    """
    return 'RU'

def detect_language_by_location(request):
    """
    Always return Russian language
    """
    return 'ru'