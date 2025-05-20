import os
import json

ROOT = os.path.join('data', 'scenes')
LANGS = ['ru', 'ky']

def add_progress_to_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        scenes = json.load(f)
    total = len(scenes)
    changed = False
    for i, scene in enumerate(scenes):
        # Только если нет или отличается
        if 'progress' not in scene or scene['progress'] != {'current': i+1, 'total': total}:
            scene['progress'] = {'current': i+1, 'total': total}
            changed = True
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(scenes, f, ensure_ascii=False, indent=2)
        print(f"[OK] {filepath} — обновлено")
    else:
        print(f"[SKIP] {filepath} — без изменений")

def main():
    for lang in LANGS:
        dirpath = os.path.join(ROOT, lang)
        for fname in os.listdir(dirpath):
            if fname.endswith('.json'):
                fpath = os.path.join(dirpath, fname)
                add_progress_to_file(fpath)

if __name__ == '__main__':
    main() 