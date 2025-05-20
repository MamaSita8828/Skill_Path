import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class Database:
    """Класс для работы с базой данных."""
    
    def __init__(self, db_file: str = "data/database.json"):
        """Инициализация базы данных."""
        self.db_file = db_file
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Проверяет существование файла базы данных и создает его при необходимости."""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'goals': {},
                    'materials': {},
                    'notes': {},
                    'users': {}
                }, f, ensure_ascii=False, indent=4)
    
    def _read_db(self) -> Dict:
        """Читает данные из базы данных."""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self._ensure_db_exists()
            return {'goals': {}, 'materials': {}, 'notes': {}, 'users': {}}
    
    def _write_db(self, data: Dict):
        """Записывает данные в базу данных."""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при записи в базу данных: {e}")
    
    def add_goal(self, user_id: int, goal_data: Dict) -> str:
        """Добавляет новую цель."""
        db = self._read_db()
        if db['goals']:
            max_id = max(int(i) for i in db['goals'].keys())
            goal_id = str(max_id + 1)
        else:
            goal_id = '1'
        goal_data['created_at'] = datetime.now().strftime("%d.%m.%Y")
        goal_data['user_id'] = user_id
        db['goals'][goal_id] = goal_data
        self._write_db(db)
        return goal_id
    
    def get_user_goals(self, user_id: int) -> List[Dict]:
        """Получает список целей пользователя."""
        db = self._read_db()
        return [
            {**goal, 'id': goal_id}
            for goal_id, goal in db['goals'].items()
            if goal['user_id'] == user_id
        ]
    
    def update_goal(self, goal_id: str, goal_data: Dict) -> bool:
        """Обновляет цель."""
        db = self._read_db()
        if goal_id not in db['goals']:
            return False
        db['goals'][goal_id].update(goal_data)
        self._write_db(db)
        return True
    
    def delete_goal(self, goal_id: str) -> bool:
        """Удаляет цель."""
        db = self._read_db()
        if goal_id not in db['goals']:
            return False
        del db['goals'][goal_id]
        self._write_db(db)
        return True
    
    def get_goal_stats(self, user_id: int) -> Dict:
        """Получает статистику по целям пользователя."""
        goals = self.get_user_goals(user_id)
        return {
            'active_goals': len([g for g in goals if g.get('progress', 0) < 100]),
            'completed_goals': len([g for g in goals if g.get('progress', 0) == 100]),
            'materials_studied': len([g for g in goals if g.get('materials', [])]),
            'study_time': sum(g.get('study_time', 0) for g in goals)
        }
    
    def add_material(self, user_id: int, material_data: Dict) -> str:
        """Добавляет новый материал."""
        db = self._read_db()
        if db['materials']:
            max_id = max(int(i) for i in db['materials'].keys())
            material_id = str(max_id + 1)
        else:
            material_id = '1'
        material_data['created_at'] = datetime.now().strftime("%d.%m.%Y")
        material_data['user_id'] = user_id
        db['materials'][material_id] = material_data
        self._write_db(db)
        return material_id
    
    def get_user_materials(self, user_id: int) -> List[Dict]:
        """Получает список материалов пользователя."""
        db = self._read_db()
        return [
            {**material, 'id': material_id}
            for material_id, material in db['materials'].items()
            if material['user_id'] == user_id
        ]
    
    def search_materials(self, user_id: int, query: str) -> List[Dict]:
        """Поиск материалов по ключевым словам."""
        materials = self.get_user_materials(user_id)
        query = query.lower()
        return [
            material for material in materials
            if query in material['title'].lower() or
               query in material['description'].lower() or
               query in material.get('category', '').lower()
        ]

# Создаем экземпляр базы данных
db = Database() 