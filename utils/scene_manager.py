import json
import os
from pathlib import Path
from typing import List, Dict, Any
import random
import re

# Абсолютный путь к папке сцен относительно этого файла
SCENES_DIR = Path(__file__).parent.parent / "data" / "scenes"

ALLOWED_PROFILES = {
    'Исследователь', 'Аналитик', 'Творец', 'Технарь', 'Коммуникатор', 'Организатор',
    'Визуальный художник', 'Цифровой художник', 'Писатель', 'Эколог', 'Ученый-естественник',
    'Социолог', 'Историк', 'Психолог', 'Инженер-системотехник', 'Программист', 'Инженер данных',
    'Робототехник', 'Инженер-конструктор', 'Электронщик', 'Программист-интерфейсов',
    'Программист серверных систем', 'Системный инженер', 'Организатор мероприятий', 'Фасилитатор',
    'PR-специалист', 'Маркетолог', 'Аналитик данных', 'Системный аналитик', 'Финансовый аналитик',
    'Логик', 'Дизайнер пространства', 'Исполнительский художник'
}

def validate_scenes_json():
    with open(SCENES_DIR / 'ru' / 'basic.json', encoding="utf-8") as f:
        data = json.load(f)
    scenes = data["translations"]["ru"]["scenes"]["basic"]
    errors = []
    scene_ids = set()
    option_ids_global = set()
    all_scene_ids = {scene['id'] for scene in scenes}
    for scene in scenes:
        # Проверка id сцены
        if scene['id'] in scene_ids:
            errors.append(f"Дублирующийся id сцены: {scene['id']}")
        scene_ids.add(scene['id'])
        # Проверка обязательных полей сцены
        for field in ['id', 'title', 'description', 'options']:
            if field not in scene:
                errors.append(f"Сцена {scene.get('id', '?')} не содержит обязательного поля '{field}'")
        # Проверка опций
        for option in scene.get('options', []):
            # Глобальная уникальность id опций
            option_global_id = f"{scene['id']}_{option['id']}"
            if option_global_id in option_ids_global:
                errors.append(f"Дублирующийся id опции (глобально): {option_global_id}")
            option_ids_global.add(option_global_id)
            # Проверка обязательных полей опции
            for field in ['id', 'text', 'profiles', 'next_scene_id', 'feedback']:
                if field not in option:
                    errors.append(f"Опция {option.get('id', '?')} в сцене {scene['id']} не содержит обязательного поля '{field}'")
            # Проверка next_scene_id
            if 'next_scene_id' in option and option['next_scene_id'] not in all_scene_ids:
                errors.append(f"Опция {option['id']} в сцене {scene['id']} ссылается на несуществующую сцену {option['next_scene_id']}")
            # Проверка профилей
            for p in option.get('profiles', []):
                if p['name'] not in ALLOWED_PROFILES:
                    errors.append(f"Профиль '{p['name']}' в опции {option['id']} сцены {scene['id']} не входит в список допустимых профилей")
                if not isinstance(p.get('weight', None), int):
                    errors.append(f"Профиль '{p['name']}' в опции {option['id']} сцены {scene['id']} имеет некорректный вес (weight)")
    if errors:
        print("Ошибки в scenes.json:")
        for err in errors:
            print("-", err)
    else:
        print("scenes.json: ошибок не найдено!")

class SceneManager:
    """
    SceneManager для профориентационного теста SkillPath:
    - Загружает сцены из отдельных файлов по языку и ветке (basic, technical, creative и т.д.)
    - Поддержка мультиязычности и гендерных плейсхолдеров
    """
    def __init__(self, language='ru', gender='male'):
        # Автоматически приводим 'kg' к 'ky' для кыргызского языка
        if language == 'kg':
            language = 'ky'
        self.language = language  # 'ru' или 'ky'
        self.gender = gender      # 'male' или 'female'

    def _load_scenes_file(self, category: str) -> List[Dict[str, Any]]:
        """Загружает список сцен из файла по языку и категории (base_scenes, technical и т.д.)"""
        filename = f"{category}_{self.language}.json"
        path = SCENES_DIR / self.language / filename
        print(f"[DEBUG] _load_scenes_file: path={path}")
        if not path.exists():
            print(f"[ERROR] Файл сцен не найден: {path}")
            # Fallback на русский язык
            fallback_path = SCENES_DIR / 'ru' / f"{category}_ru.json"
            if fallback_path.exists():
                print(f"[INFO] Использую fallback: {fallback_path}")
                path = fallback_path
            else:
                raise FileNotFoundError(f"Файл сцен не найден: {path}")
        with open(path, encoding="utf-8") as f:
            scenes = json.load(f)
        print(f"[DEBUG] _load_scenes_file: загружено {len(scenes)} сцен из {path}")
        # Обработка гендерных плейсхолдеров
        for scene in scenes:
            scene["description"] = self._replace_gender_placeholders(scene.get("description", ""))
            for option in scene.get("options", []):
                option["text"] = self._replace_gender_placeholders(option.get("text", ""))
        return scenes

    def _replace_gender_placeholders(self, text: str) -> str:
        """Заменяет гендерные плейсхолдеры в тексте в зависимости от выбранного пола"""
        def replace_gender_match(match):
            match_parts = match.group(1).split('|')
            return match_parts[0] if self.gender == 'male' else match_parts[1]
        pattern = r'{gender:([^}]+)}'
        return re.sub(pattern, replace_gender_match, text)

    def get_basic_scenes(self) -> List[Dict[str, Any]]:
        """Возвращает 6 базовых сцен (base_scenes)"""
        scenes = self._load_scenes_file("base_scenes")
        print(f"[DEBUG] get_basic_scenes: загружено {len(scenes)} сцен")
        return scenes[:6]

    def get_personal_scenes_by_branch(self, branch: str, count: int = 11) -> list[dict]:
        """
        Загружает персональные сцены для профиля/направления (branch/profile_name) по языку.
        Например: branch='Техническая', язык='ru' -> data/scenes/ru/technical_ru.json
        """
        print(f"[DEBUG] get_personal_scenes_by_branch: branch={branch}, lang={self.language}")
        lang = self.language
        profile_to_file = {
            'Техническая': f'technical_{lang}.json',
            'Гуманитарная': f'humanitarian_{lang}.json',
            'Естественно-научная': f'natural_science_{lang}.json',
            'Социально-экономическая': f'social_economic_{lang}.json',
            'Творческо-художественная': f'creative_art_{lang}.json',
            'Прикладно-технологическая': f'applied_technology_{lang}.json',
        }
        filename = profile_to_file.get(branch)
        print(f"[DEBUG] profile_to_file.get(branch)={filename}")
        if not filename:
            print(f"[SceneManager] Не найден маппинг для профиля: {branch}")
            return []
        file_path = f"data/scenes/{lang}/{filename}"
        print(f"[DEBUG] Открываю файл: {file_path}")
        try:
            with open(file_path, encoding="utf-8") as f:
                scenes = json.load(f)
            print(f"[DEBUG] Загружено сцен: {len(scenes)} из файла {file_path}")
            return scenes[:count]
        except Exception as e:
            print(f"[SceneManager] Не найден файл ветки: {file_path} ({e})")
            return []

    def change_language(self, language: str):
        # Автоматически приводим 'kg' к 'ky' для кыргызского языка
        if language == 'kg':
            language = 'ky'
        if language in ['ru', 'ky']:
            self.language = language

    def change_gender(self, gender: str):
        if gender in ['male', 'female']:
            self.gender = gender

    def get_scene_by_id(self, scene_id: int) -> Dict[str, Any]:
        """Возвращает сцену по id из любой ветки (base_scenes, technical, social_economic и т.д.)"""
        # Сначала ищем в базовых сценах
        scenes = self._load_scenes_file("base_scenes")
        for scene in scenes:
            if scene['id'] == scene_id:
                return scene
        # Затем ищем во всех ветках
        for branch in [
            "technical",
            "social_economic",
            "natural_science",
            "applied_technology",
            "creative_art",
            "humanitarian"
        ]:
            try:
                scenes = self._load_scenes_file(branch)
                for scene in scenes:
                    if scene['id'] == scene_id:
                        return scene
            except FileNotFoundError:
                continue
        return None

# Инициализация менеджера сцен с русским языком и мужским полом по умолчанию
scene_manager = SceneManager(language='ru', gender='male')

# Для тестирования
if __name__ == "__main__":
    # Русский, мужской пол
    sm = SceneManager(language='ru', gender='male')
    scene = sm.get_scene(1)
    print(f"RU/Male: {scene['description']}")
    
    # Русский, женский пол
    sm.change_gender('female')
    scene = sm.get_scene(1)
    print(f"RU/Female: {scene['description']}")
    
    # Кыргызский, мужской пол
    sm.change_language('ky')
    sm.change_gender('male')
    scene = sm.get_scene(1)
    print(f"KY/Male: {scene['description']}")
    
    # Кыргызский, женский пол
    sm.change_gender('female')
    scene = sm.get_scene(1)
    print(f"KY/Female: {scene['description']}")