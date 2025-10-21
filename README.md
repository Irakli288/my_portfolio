# Портфолио Иракли Кекелашвили

Современное портфолио веб-разработчика с админ-панелью и Telegram-ботом для управления.

## 📥 Клонирование репозитория

```bash
git clone https://github.com/Irakli288/my_portfolio.git
cd my_portfolio
```

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Укажите в `.env`:
- `TELEGRAM_BOT_TOKEN` - токен вашего бота от @BotFather
- `ADMIN_TELEGRAM_ID` - ваш Telegram ID (узнать у @userinfobot)
- `TELEGRAM_BOT_URL` - ссылка на вашего бота (например, https://t.me/your_bot)
- `SECRET_KEY` - секретный ключ для Flask

### 3.0 Запуск приложения сразу (игнорировать всё дальше)

```bash
./run_local.sh
```

### 3. Запуск приложения

```bash
python app.py
```

Сайт будет доступен по адресу: http://localhost:5000

### 4. Запуск Telegram бота

В отдельном терминале:

```bash
python bot.py
```

## Возможности

- 📱 Адаптивный дизайн
- 🔐 Авторизация через Telegram
- 👑 Админ-панель для управления проектами
- 🏷️ Система тегов для фильтрации проектов
- 🤖 Telegram бот для управления доступом

## Технологии

- Flask
- SQLite
- python-telegram-bot
- Vanilla JavaScript

## Контакты

- Email: Iraklikekelashvili32@gmail.com
- Telegram: [@BOMBAKLI](https://t.me/BOMBAKLI)
- GitHub: [Irakli288](https://github.com/Irakli288)
