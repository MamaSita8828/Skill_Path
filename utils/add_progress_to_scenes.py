import os
import json
from glob import glob

SCENES_DIR = os.path.join(os.path.dirname(__file__), '../data/scenes')

def convert_profile_to_profiles(scene):
    # Конвертирует старый формат profile -> profiles
    if 'profile' in scene:
        scene['profiles'] = [{"name": scene['profile'], "weight": 1}]
        del scene['profile']
    # Конвертируем опции
    for option in scene.get('options', []):
        if 'profile' in option:
            option['profiles'] = [{"name": option['profile'], "weight": 1}]
            del option['profile']
    return scene

def process_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    # Если это массив сцен
    if isinstance(data, list):
        ids = set()
        for scene in data:
            # Проверка на дубли id
            if scene['id'] in ids:
                print(f"Дублирующийся id {scene['id']} в файле {filepath}")
            ids.add(scene['id'])
            convert_profile_to_profiles(scene)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Файл {filepath} обработан и сохранён.")
    else:
        print(f"Пропущен файл (не массив): {filepath}")

def main():
    for lang in ['ru', 'ky']:
        for file in glob(f"{SCENES_DIR}/{lang}/*.json"):
            process_file(file)

if __name__ == "__main__":
    main() 