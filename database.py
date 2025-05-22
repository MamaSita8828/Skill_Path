import aiomysql
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Database:
    def __init__(self):
        self.pool = None
        
    async def connect(self):
        """Создание пула соединений с базой данных"""
        self.pool = await aiomysql.create_pool(
            host=os.getenv('MYSQL_HOST', 'turntable.proxy.rlwy.net'),
            port=int(os.getenv('MYSQL_PORT', 11725)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'obyRyMEAMtDgJsSxGkontTXPZzwJdtFR'),
            db=os.getenv('MYSQL_DB', 'railway'),
            charset='utf8mb4',
            autocommit=True,
            maxsize=10,
            minsize=1
        )
        print("✅ Подключение к базе данных установлено")
    
    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
    
    async def execute_query(self, query: str, params: tuple = None):
        """Выполнение запроса без возврата данных"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return cursor.rowcount
    
    async def fetch_one(self, query: str, params: tuple = None):
        """Выполнение запроса с возвратом одной записи"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: tuple = None):
        """Выполнение запроса с возвратом всех записей"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()

# Создаем глобальный экземпляр базы данных
db = Database()

class UserManager:
    """Управление пользователями"""
    
    @staticmethod
    async def create_user(telegram_id: int, fio: str, **kwargs) -> bool:
        """Создание нового пользователя"""
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
            kwargs.get('artifacts', ''),
            kwargs.get('opened_profiles', '')
        )
        
        try:
            await db.execute_query(query, params)
            print(f"✅ Пользователь {telegram_id} создан")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания пользователя: {e}")
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
            print(f"❌ Ошибка обновления пользователя: {e}")
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
            print(f"❌ Ошибка сохранения прогресса: {e}")
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
                print(f"❌ Ошибка парсинга JSON для пользователя {telegram_id}")
        
        return progress
    
    @staticmethod
    async def delete_progress(telegram_id: int) -> bool:
        """Удаление прогресса (при завершении теста)"""
        query = "DELETE FROM test_progress WHERE telegram_id = %s"
        try:
            rows_affected = await db.execute_query(query, (telegram_id,))
            return rows_affected > 0
        except Exception as e:
            print(f"❌ Ошибка удаления прогресса: {e}")
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
            print(f"✅ Результат сохранен для пользователя {telegram_id}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения результата: {e}")
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
            print(f"❌ Ошибка добавления цели: {e}")
            return False

    @staticmethod
    async def get_user_goals(telegram_id: int) -> list:
        """Получить все цели пользователя"""
        query = "SELECT * FROM goals WHERE telegram_id = %s ORDER BY created_at DESC"
        try:
            return await db.fetch_all(query, (telegram_id,))
        except Exception as e:
            print(f"❌ Ошибка получения целей: {e}")
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
            print(f"❌ Ошибка получения статистики целей: {e}")
            return {"active_goals": 0, "completed_goals": 0, "materials_studied": 0, "study_time": 0} 