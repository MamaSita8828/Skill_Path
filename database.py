import aiomysql
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
import re
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

def parse_mysql_url(url):
    """Парсинг MYSQL_URL в параметры подключения"""
    try:
        # Пример: mysql://user:pass@host:port/dbname
        regex = r"mysql:\/\/(.*?):(.*?)@(.*?):(\d+)\/(.*)"
        match = re.match(regex, url)
        if not match:
            raise ValueError("MYSQL_URL не соответствует формату mysql://user:pass@host:port/dbname")
        user, password, host, port, db = match.groups()
        return {
            "user": user,
            "password": password,
            "host": host,
            "port": int(port),
            "db": db
        }
    except Exception as e:
        logger.error(f"❌ Ошибка парсинга MYSQL_URL: {e}")
        raise

# Получаем параметры подключения
mysql_url = os.getenv("MYSQL_URL")
if not mysql_url:
    raise ValueError("MYSQL_URL не найден в переменных окружения")

db_params = parse_mysql_url(mysql_url)

class Database:
    def __init__(self):
        self.pool = None
        self.max_retries = 5
        self.retry_delay = 5  # секунды
        
    async def ensure_connection(self):
        """Проверка и восстановление подключения к БД"""
        if not self.pool:
            await self.connect()
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
        except Exception as e:
            logger.error(f"❌ Ошибка проверки подключения: {e}")
            await self.reconnect()
        
    async def reconnect(self):
        """Переподключение к базе данных"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
        self.pool = None
        await self.connect()
        
    async def connect(self):
        """Создание пула соединений с базой данных и инициализация таблиц"""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                self.pool = await aiomysql.create_pool(
                    host=db_params["host"],
                    port=db_params["port"],
                    user=db_params["user"],
                    password=db_params["password"],
                    db=db_params["db"],
                    charset='utf8mb4',
                    autocommit=True,
                    maxsize=10,
                    minsize=1,
                    connect_timeout=10
                )
                logger.info("✅ Подключение к базе данных установлено")
                
                # Создаем таблицы при подключении
                await self.create_tables()
                return
                
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ Попытка {retry_count}/{self.max_retries} подключения к БД не удалась: {e}")
                if retry_count < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise Exception(f"Не удалось подключиться к БД после {self.max_retries} попыток")

    async def create_tables(self):
        """Создание необходимых таблиц, если они не существуют"""
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNSIGNED UNIQUE,
                    fio VARCHAR(255),
                    school VARCHAR(255),
                    class_number INT,
                    class_letter VARCHAR(10),
                    gender VARCHAR(10),
                    birth_year INT,
                    city VARCHAR(255),
                    language VARCHAR(20),
                    artifacts TEXT,
                    opened_profiles TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            'test_progress': """
                CREATE TABLE IF NOT EXISTS test_progress (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNSIGNED,
                    current_scene VARCHAR(255),
                    all_scenes TEXT,
                    profile_scores TEXT,
                    profession_scores TEXT,
                    lang VARCHAR(10),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            'test_results': """
                CREATE TABLE IF NOT EXISTS test_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNSIGNED,
                    finished_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    profile VARCHAR(255),
                    score INT,
                    details TEXT,
                    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            'goals': """
                CREATE TABLE IF NOT EXISTS goals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNSIGNED,
                    title VARCHAR(255),
                    description TEXT,
                    deadline DATE,
                    priority INT,
                    progress INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        }
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    for table_name, create_query in tables.items():
                        try:
                            await cursor.execute(create_query)
                            logger.info(f"✅ Таблица {table_name} проверена/создана")
                        except Exception as e:
                            logger.error(f"❌ Ошибка создания таблицы {table_name}: {e}")
                            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при создании таблиц: {e}")
            raise

    async def execute_query(self, query: str, params: tuple = None):
        """Выполнение запроса без возврата данных"""
        await self.ensure_connection()
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения запроса: {e}")
            raise

    async def fetch_one(self, query: str, params: tuple = None):
        """Выполнение запроса с возвратом одной записи"""
        await self.ensure_connection()
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    return await cursor.fetchone()
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных: {e}")
            raise

    async def fetch_all(self, query: str, params: tuple = None):
        """Выполнение запроса с возвратом всех записей"""
        await self.ensure_connection()
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    return await cursor.fetchall()
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных: {e}")
            raise

    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("✅ Соединение с базой данных закрыто")

# Создаем глобальный экземпляр базы данных
db = Database()

class UserManager:
    """Управление пользователями"""
    
    @staticmethod
    async def create_user(telegram_id: int, fio: str, **kwargs) -> bool:
        """Создание нового пользователя"""
        try:
            # Ensure telegram_id is a positive integer
            telegram_id = abs(int(telegram_id))
            logger.info(f"Creating user with telegram_id: {telegram_id} (type: {type(telegram_id)})")
            
            # First check if user exists
            existing_user = await UserManager.get_user(telegram_id)
            if existing_user:
                logger.info(f"User {telegram_id} already exists")
                return True
            
            query = """
            INSERT INTO users (telegram_id, fio, school, class_number, class_letter, 
                              gender, birth_year, city, language, artifacts, opened_profiles)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                telegram_id,
                fio,
                kwargs.get('school', ''),
                kwargs.get('class_number', None),
                kwargs.get('class_letter', ''),
                kwargs.get('gender', ''),
                kwargs.get('birth_year', None),
                kwargs.get('city', ''),
                kwargs.get('language', 'ru'),
                json.dumps(kwargs.get('artifacts', []), ensure_ascii=False),
                json.dumps(kwargs.get('opened_profiles', []), ensure_ascii=False)
            )
            
            try:
                # Ensure tables have correct column types
                await db.execute_query("""
                    ALTER TABLE users 
                    MODIFY COLUMN telegram_id BIGINT UNSIGNED UNIQUE
                """)
                await db.execute_query("""
                    ALTER TABLE test_progress 
                    MODIFY COLUMN telegram_id BIGINT UNSIGNED
                """)
                await db.execute_query("""
                    ALTER TABLE test_results 
                    MODIFY COLUMN telegram_id BIGINT UNSIGNED
                """)
                await db.execute_query("""
                    ALTER TABLE goals 
                    MODIFY COLUMN telegram_id BIGINT UNSIGNED
                """)
                
                # Create user
                await db.execute_query(query, params)
                logger.info(f"✅ User {telegram_id} created successfully")
                return True
            except Exception as e:
                logger.error(f"❌ Error creating user: {e}")
                if "Duplicate entry" in str(e):
                    logger.info(f"User {telegram_id} already exists (duplicate entry)")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Error in create_user: {e}")
            return False
    
    @staticmethod
    async def get_user(telegram_id: int) -> Optional[Dict]:
        """Получение пользователя по telegram_id"""
        query = "SELECT * FROM users WHERE telegram_id = %s"
        return await db.fetch_one(query, (telegram_id,))
    
    @staticmethod
    async def update_user(telegram_id: int, **kwargs) -> bool:
        """Обновление данных пользователя"""
        # Формируем запрос динамически
        set_clauses = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['fio', 'school', 'class_number', 'class_letter', 
                      'gender', 'birth_year', 'city', 'language', 'artifacts', 'opened_profiles']:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            return False
            
        params.append(telegram_id)
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE telegram_id = %s"
        
        try:
            rows_affected = await db.execute_query(query, tuple(params))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"❌ Ошибка обновления пользователя: {e}")
            return False

class TestProgressManager:
    """Управление прогрессом тестирования"""
    
    @staticmethod
    async def save_progress(telegram_id: int, current_scene: str, 
                           all_scenes: List[str] = None, 
                           profile_scores: Dict = None,
                           profession_scores: Dict = None,
                           lang: str = 'ru') -> bool:
        """Сохранение прогресса тестирования"""
        
        # Проверяем, есть ли уже запись
        existing = await db.fetch_one(
            "SELECT id FROM test_progress WHERE telegram_id = %s", 
            (telegram_id,)
        )
        
        all_scenes_json = json.dumps(all_scenes or [], ensure_ascii=False)
        profile_scores_json = json.dumps(profile_scores or {}, ensure_ascii=False)
        profession_scores_json = json.dumps(profession_scores or {}, ensure_ascii=False)
        
        if existing:
            # Обновляем существующую запись
            query = """
            UPDATE test_progress 
            SET current_scene = %s, all_scenes = %s, profile_scores = %s, 
                profession_scores = %s, lang = %s, updated_at = NOW()
            WHERE telegram_id = %s
            """
            params = (current_scene, all_scenes_json, profile_scores_json, 
                     profession_scores_json, lang, telegram_id)
        else:
            # Создаем новую запись
            query = """
            INSERT INTO test_progress (telegram_id, current_scene, all_scenes, 
                                     profile_scores, profession_scores, lang, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            params = (telegram_id, current_scene, all_scenes_json, 
                     profile_scores_json, profession_scores_json, lang)
        
        try:
            await db.execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения прогресса: {e}")
            return False
    
    @staticmethod
    async def get_progress(telegram_id: int) -> Optional[Dict]:
        """Получение прогресса пользователя"""
        query = "SELECT * FROM test_progress WHERE telegram_id = %s"
        progress = await db.fetch_one(query, (telegram_id,))
        
        if progress:
            # Парсим JSON поля
            try:
                progress['all_scenes'] = json.loads(progress['all_scenes'] or '[]')
                progress['profile_scores'] = json.loads(progress['profile_scores'] or '{}')
                progress['profession_scores'] = json.loads(progress['profession_scores'] or '{}')
            except json.JSONDecodeError:
                logger.error(f"❌ Ошибка парсинга JSON для пользователя {telegram_id}")
        
        return progress
    
    @staticmethod
    async def delete_progress(telegram_id: int) -> bool:
        """Удаление прогресса (при завершении теста)"""
        query = "DELETE FROM test_progress WHERE telegram_id = %s"
        try:
            rows_affected = await db.execute_query(query, (telegram_id,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"❌ Ошибка удаления прогресса: {e}")
            return False

class TestResultsManager:
    """Управление результатами тестов"""
    
    @staticmethod
    async def save_result(telegram_id: int, profile: str, score: int, 
                         details: Dict = None) -> bool:
        """Сохранение результата теста"""
        query = """
        INSERT INTO test_results (telegram_id, finished_at, profile, score, details)
        VALUES (%s, NOW(), %s, %s, %s)
        """
        
        details_json = json.dumps(details or {}, ensure_ascii=False)
        params = (telegram_id, profile, score, details_json)
        
        try:
            await db.execute_query(query, params)
            logger.info(f"✅ Результат сохранен для пользователя {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результата: {e}")
            return False
    
    @staticmethod
    async def get_user_results(telegram_id: int) -> List[Dict]:
        """Получение всех результатов пользователя"""
        query = """
        SELECT * FROM test_results 
        WHERE telegram_id = %s 
        ORDER BY finished_at DESC
        """
        results = await db.fetch_all(query, (telegram_id,))
        
        # Парсим JSON поля
        for result in results:
            try:
                result['details'] = json.loads(result['details'] or '{}')
            except json.JSONDecodeError:
                logger.error(f"❌ Ошибка парсинга JSON в get_user_results для пользователя {telegram_id}")
                result['details'] = {}
        
        return results
    
    @staticmethod
    async def get_latest_result(telegram_id: int) -> Optional[Dict]:
        """Получение последнего результата пользователя"""
        query = """
        SELECT * FROM test_results 
        WHERE telegram_id = %s 
        ORDER BY finished_at DESC 
        LIMIT 1
        """
        result = await db.fetch_one(query, (telegram_id,))
        
        if result:
            try:
                result['details'] = json.loads(result['details'] or '{}')
            except json.JSONDecodeError:
                logger.error(f"❌ Ошибка парсинга JSON в get_latest_result для пользователя {telegram_id}")
                result['details'] = {}
        
        return result 

class GoalManager:
    """Управление целями пользователя"""

    @staticmethod
    async def add_goal(telegram_id: int, title: str, description: str, deadline: str, priority: int) -> bool:
        """Добавить новую цель"""
        query = """
        INSERT INTO goals (telegram_id, title, description, deadline, priority, progress, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        params = (telegram_id, title, description, deadline, priority, 0)
        try:
            await db.execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка добавления цели: {e}")
            return False

    @staticmethod
    async def get_user_goals(telegram_id: int) -> list:
        """Получить все цели пользователя"""
        query = "SELECT * FROM goals WHERE telegram_id = %s ORDER BY created_at DESC"
        try:
            return await db.fetch_all(query, (telegram_id,))
        except Exception as e:
            logger.error(f"❌ Ошибка получения целей: {e}")
            return []

    @staticmethod
    async def get_goal_stats(telegram_id: int) -> dict:
        """Получить статистику по целям пользователя"""
        query_active = "SELECT COUNT(*) as cnt FROM goals WHERE telegram_id = %s AND progress < 100"
        query_completed = "SELECT COUNT(*) as cnt FROM goals WHERE telegram_id = %s AND progress >= 100"
        try:
            active = await db.fetch_one(query_active, (telegram_id,))
            completed = await db.fetch_one(query_completed, (telegram_id,))
            # Здесь можно добавить другие параметры статистики
            return {
                "active_goals": active["cnt"] if active else 0,
                "completed_goals": completed["cnt"] if completed else 0,
                "materials_studied": 0,  # Можно реализовать позже
                "study_time": 0           # Можно реализовать позже
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики целей: {e}")
            return {"active_goals": 0, "completed_goals": 0, "materials_studied": 0, "study_time": 0} 