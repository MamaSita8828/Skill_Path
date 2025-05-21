from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    telegram_id: int
    fio: Optional[str] = None
    school: Optional[str] = None
    class_number: Optional[int] = None
    class_letter: Optional[str] = None
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    city: Optional[str] = None
    language: Optional[str] = None
    artifacts: Optional[str] = None  # JSON-строка с коллекцией артефактов
    opened_profiles: Optional[str] = None  # JSON-строка с открытыми порталами

class TestResult(BaseModel):
    id: Optional[int] = None
    telegram_id: int
    finished_at: Optional[str] = None  # ISO8601 datetime
    profile: Optional[str] = None
    score: Optional[int] = None
    details: Optional[str] = None  # JSON или текст с деталями

class TestProgress(BaseModel):
    id: Optional[int] = None
    telegram_id: int
    current_scene: int
    all_scenes: str  # JSON-строка со всеми сценами
    profile_scores: Optional[str] = None  # JSON-строка
    profession_scores: Optional[str] = None  # JSON-строка
    lang: Optional[str] = None
    updated_at: Optional[str] = None  # ISO8601 datetime