# SkillPath Bot

Telegram бот для управления и отслеживания прогресса в обучении.

## Описание

SkillPath Bot - это Telegram бот, разработанный для помощи пользователям в отслеживании их прогресса обучения и управления образовательными целями.

## Установка

1. Клонируйте репозиторий:
```bash
# git clone <ваш-репозиторий>
cd skillpath-bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv .venv
# Для Windows:
.venv\Scripts\activate
# Для Linux/Mac:
source .venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env на основе .env.example и заполните необходимые переменные окружения:
```bash
cp .env.example .env
```

5. Запустите бота:
```bash
python bot.py
```

## Пример .env.example

```
BOT_TOKEN=ваш_токен_бота
ADMIN_ID=123456789
DEBUG=False
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
LOG_LEVEL=INFO
LOG_FILE=bot.log
ADMIN_IDS=123456789,987654321
```

## Структура проекта

```
skillpath-bot/
├── handlers/         # Обработчики команд и сообщений
├── utils/           # Вспомогательные функции
├── data/            # Данные и конфигурации
├── tests/           # Тесты
├── bot.py           # Основной файл бота
├── requirements.txt # Зависимости проекта
└── README.md        # Документация
```

## Разработка

### Запуск тестов
```bash
pytest
```

### Линтинг
```bash
flake8
```

## Лицензия

MIT

## Запуск бота и backend

1. Установите зависимости:
   ```
pip install -r requirements.txt
   ```
2. Запустите backend (FastAPI):
   ```
uvicorn api.main:app --reload
   ```
3. Запустите бота:
   ```
python bot.py
   ```

## Структура
- `api/` — backend (FastAPI)
- `handlers/` — обработчики aiogram
- `utils/` — утилиты и вспомогательные модули
- `data/` — данные и сцены 