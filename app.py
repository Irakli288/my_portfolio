from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from database import (
    init_db, insert_sample_data, get_all_projects, get_project_by_id,
    add_project, update_project, delete_project,
    get_auth_session, is_admin_user, reject_auth_session,
    get_all_tags, add_tag, delete_tag, get_project_tags, set_project_tags, get_projects_by_tag
)
from translations import get_user_language, get_translations, detect_language_by_location

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')  # Change this in production

# Get Telegram bot URL from environment
TELEGRAM_BOT_URL = os.getenv('TELEGRAM_BOT_URL', 'https://t.me/your_bot_username')

# Configuration
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'admin_token' not in session:
            return redirect(url_for('admin_login'))

        # Verify session is still valid
        auth_session = get_auth_session(session['admin_token'])
        if not auth_session or auth_session['status'] != 'approved':
            session.clear()
            flash('Сессия истекла. Войдите заново.', 'error')
            return redirect(url_for('admin_login'))

        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Initialize database on app start
init_db()
insert_sample_data()

@app.route('/')
def index():
    # Always use Russian language
    lang = 'ru'
    translations = get_translations(lang)

    # Get tag filter if specified
    tag_id = request.args.get('tag', type=int)
    if tag_id:
        projects = get_projects_by_tag(tag_id)
    else:
        projects = get_all_projects()

    # Add tags to each project
    for project in projects:
        project['tags'] = get_project_tags(project['id'])

    tags = get_all_tags()

    return render_template('index.html', projects=projects, t=translations, lang=lang, tags=tags, selected_tag=tag_id)

@app.route('/project/<int:project_id>')
def get_project(project_id):
    project = get_project_by_id(project_id)
    if project:
        return jsonify(project)
    return jsonify({'error': 'Project not found'}), 404

@app.route('/api/request_access', methods=['POST'])
def request_access():
    """Create auth session and notify admin"""
    import uuid
    import json
    from urllib import request as urlreq
    from urllib.error import URLError

    # Generate session token
    token = str(uuid.uuid4())

    # Get user info from request
    user_agent = request.headers.get('User-Agent', 'Unknown')
    ip_address = request.remote_addr

    # Create session in database
    from database import create_auth_session
    create_auth_session(token, 0, f"Web User from {ip_address}")

    # Send request to Telegram bot admin
    BOT_TOKEN = "8486309645:AAHGj8DkNk6vGRY2p8yFGTA9_xWxfv8g8Xs"
    ADMIN_ID = 180587749

    try:
        message = (
            f"🔐 Запрос доступа к админ-панели\n\n"
            f"🌐 IP: {ip_address}\n"
            f"🖥️ User Agent: {user_agent[:50]}...\n"
            f"🔑 Session: {token[:8]}...\n\n"
            f"Разрешить доступ?"
        )

        payload = {
            "chat_id": ADMIN_ID,
            "text": message,
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "✅ Разрешить", "callback_data": f"approve_{token}"},
                    {"text": "❌ Отклонить", "callback_data": f"deny_{token}"}
                ]]
            }
        }

        req = urlreq.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        urlreq.urlopen(req, timeout=5)
    except (URLError, Exception) as e:
        print(f"Failed to send Telegram message: {e}")

    return jsonify({'token': token, 'status': 'pending'})

@app.route('/api/check_auth/<token>')
def check_auth_status(token):
    """API endpoint to check authentication status"""
    auth_session = get_auth_session(token)

    if not auth_session:
        return jsonify({'status': 'invalid'})

    return jsonify({
        'status': auth_session['status'],
        'username': auth_session['username']
    })

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Handle GET request with token parameter (auto-login)
    if request.method == 'GET':
        token = request.args.get('token')
        auto = request.args.get('auto')

        if token and auto:
            # Auto-login from polling
            auth_session = get_auth_session(token)
            if auth_session and auth_session['status'] == 'approved':
                # Set session
                session['admin_token'] = token
                session['admin_user_id'] = auth_session['telegram_user_id']
                session['username'] = auth_session['username']
                return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        token = request.form.get('token')

        if not token:
            flash('Введите токен авторизации', 'error')
            return render_template('admin_login.html', bot_url=TELEGRAM_BOT_URL)

        # Check if token is valid
        auth_session = get_auth_session(token)
        if not auth_session:
            flash('Неверный или истекший токен', 'error')
            return render_template('admin_login.html', bot_url=TELEGRAM_BOT_URL)

        if auth_session['status'] != 'approved':
            flash('Токен еще не подтвержден администратором', 'error')
            return render_template('admin_login.html', bot_url=TELEGRAM_BOT_URL)

        # Set session
        session['admin_token'] = token
        session['admin_user_id'] = auth_session['telegram_user_id']
        session['username'] = auth_session['username']

        flash('Успешный вход в админ-панель!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html', bot_url=TELEGRAM_BOT_URL)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Вы вышли из админ-панели', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    projects = get_all_projects()
    # Add tags to each project
    for project in projects:
        project['tags'] = get_project_tags(project['id'])

    tags = get_all_tags()
    return render_template('admin_dashboard.html', projects=projects, tags=tags)

@app.route('/admin', methods=['POST'])
@login_required
def admin_dashboard_post():
    action = request.form.get('action')

    if action == 'save':
        # Save project (add or update)
        project_id = request.form.get('project_id')
        title = request.form.get('title')
        description = request.form.get('description')
        full_description = request.form.get('full_description')
        live_url = request.form.get('live_url')

        # Get selected tags
        tag_ids = request.form.getlist('tags')
        tag_ids = [int(tag_id) for tag_id in tag_ids if tag_id]

        # Handle file upload
        preview_image = None
        if 'preview_image' in request.files:
            file = request.files['preview_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                import time
                filename = f"{int(time.time())}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                preview_image = f"/static/images/{filename}"

        if project_id:  # Update existing project
            # Keep existing image if no new one uploaded
            if not preview_image:
                existing_project = get_project_by_id(int(project_id))
                preview_image = existing_project['preview_image'] if existing_project else '/static/images/placeholder.jpg'

            update_project(int(project_id), title, description, full_description, preview_image, live_url)
            set_project_tags(int(project_id), tag_ids)
            flash('Проект успешно обновлен!', 'success')
        else:  # Add new project
            if not preview_image:
                preview_image = '/static/images/placeholder.jpg'

            new_project_id = add_project(title, description, full_description, preview_image, live_url)
            set_project_tags(new_project_id, tag_ids)
            flash('Проект успешно добавлен!', 'success')

    elif action == 'delete':
        # Delete project
        project_id = request.form.get('project_id')
        if project_id:
            delete_project(int(project_id))
            flash('Проект успешно удален!', 'success')

    elif action == 'add_tag':
        # Add new tag
        tag_name = request.form.get('tag_name')
        if tag_name:
            tag_id = add_tag(tag_name.strip())
            if tag_id:
                flash(f'Тег "{tag_name}" успешно добавлен!', 'success')
            else:
                flash(f'Тег "{tag_name}" уже существует!', 'error')

    elif action == 'delete_tag':
        # Delete tag
        tag_id = request.form.get('tag_id')
        if tag_id:
            delete_tag(int(tag_id))
            flash('Тег успешно удален!', 'success')

    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')