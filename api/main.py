from fastapi import FastAPI, Query
from .models import User, TestResult
from .db import get_connection

app = FastAPI()

@app.post("/users/")
def create_or_update_user(user: User):
    conn = get_connection()
    cursor = conn.cursor()
    # Создаём таблицу, если не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            fio VARCHAR(255),
            school VARCHAR(255),
            class_number INT,
            class_letter VARCHAR(10),
            gender VARCHAR(10),
            birth_year INT,
            city VARCHAR(255),
            language VARCHAR(20)
        )
    """)
    # Вставка или обновление
    cursor.execute("""
        INSERT INTO users (telegram_id, fio, school, class_number, class_letter, gender, birth_year, city, language)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            fio=VALUES(fio),
            school=VALUES(school),
            class_number=VALUES(class_number),
            class_letter=VALUES(class_letter),
            gender=VALUES(gender),
            birth_year=VALUES(birth_year),
            city=VALUES(city),
            language=VALUES(language)
    """, (
        user.telegram_id, user.fio, user.school, user.class_number, user.class_letter,
        user.gender, user.birth_year, user.city, user.language
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@app.get("/users/")
def get_user(telegram_id: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return user
    return {}

@app.post("/test_results/")
def save_test_result(result: TestResult):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            telegram_id BIGINT,
            finished_at DATETIME,
            profile VARCHAR(255),
            score INT,
            details TEXT
        )
    """)
    cursor.execute(
        """
        INSERT INTO test_results (telegram_id, finished_at, profile, score, details)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (result.telegram_id, result.finished_at, result.profile, result.score, result.details)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@app.get("/test_results/")
def get_test_results(telegram_id: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM test_results WHERE telegram_id = %s ORDER BY finished_at DESC", (telegram_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results