import asyncio
import aiomysql

async def check_table_structure():
    print("🔍 Проверка структуры таблиц...")
    
    try:
        connection = await aiomysql.connect(
            host='turntable.proxy.rlwy.net',
            port=11725,
            user='root',
            password='obyRyMEAMtDgJsSxGkontTXPZzwJdtFR',
            db='railway',
            charset='utf8mb4'
        )
        
        async with connection.cursor() as cursor:
            
            # Список таблиц для проверки
            tables = ['users', 'test_progress', 'test_results', 'goals']
            
            for table_name in tables:
                print(f"\n📋 Таблица: {table_name}")
                print("=" * 50)
                
                try:
                    # Структура таблицы
                    await cursor.execute(f"DESCRIBE {table_name}")
                    columns = await cursor.fetchall()
                    
                    print("Колонки:")
                    for column in columns:
                        field, type_, null, key, default, extra = column
                        key_info = f" [{key}]" if key else ""
                        null_info = " (NULL)" if null == "YES" else " (NOT NULL)"
                        default_info = f" DEFAULT: {default}" if default else ""
                        extra_info = f" {extra}" if extra else ""
                        
                        print(f"  • {field}: {type_}{key_info}{null_info}{default_info}{extra_info}")
                    
                    # Количество записей
                    await cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = await cursor.fetchone()
                    print(f"\n📊 Записей в таблице: {count[0]}")
                    
                    # Показать несколько примеров данных (если есть)
                    if count[0] > 0:
                        await cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        rows = await cursor.fetchall()
                        print(f"\nПример данных (первые {len(rows)} записи):")
                        for i, row in enumerate(rows, 1):
                            print(f"  {i}. {row}")
                    
                except Exception as e:
                    print(f"❌ Ошибка при проверке таблицы {table_name}: {e}")
            
            # Проверка внешних ключей
            print(f"\n🔗 Проверка внешних ключей...")
            await cursor.execute("""
                SELECT 
                    TABLE_NAME, 
                    COLUMN_NAME, 
                    REFERENCED_TABLE_NAME, 
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = 'railway' 
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            
            foreign_keys = await cursor.fetchall()
            if foreign_keys:
                for fk in foreign_keys:
                    print(f"  • {fk[0]}.{fk[1]} → {fk[2]}.{fk[3]}")
            else:
                print("  Внешние ключи не найдены")
        
        connection.close()
        
        print(f"\n" + "=" * 60)
        print("✅ Проверка структуры завершена!")
        print("💡 Теперь можно приступать к интеграции с ботом")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def check_compatibility():
    """Проверка совместимости структуры с нашим кодом"""
    
    print(f"\n🔧 Проверка совместимости структуры...")
    
    # Ожидаемые колонки для каждой таблицы
    expected_columns = {
        'users': [
            'id', 'telegram_id', 'fio', 'school', 'class_number', 
            'class_letter', 'gender', 'birth_year', 'city', 
            'language', 'artifacts', 'opened_profiles'
        ],
        'test_progress': [
            'id', 'telegram_id', 'current_scene', 'all_scenes',
            'profile_scores', 'profession_scores', 'lang', 'updated_at'
        ],
        'test_results': [
            'id', 'telegram_id', 'finished_at', 'profile', 'score', 'details'
        ]
    }
    
    try:
        connection = await aiomysql.connect(
            host='turntable.proxy.rlwy.net',
            port=11725,
            user='root',
            password='obyRyMEAMtDgJsSxGkontTXPZzwJdtFR',
            db='railway',
            charset='utf8mb4'
        )
        
        async with connection.cursor() as cursor:
            
            compatibility_issues = []
            
            for table_name, expected_cols in expected_columns.items():
                print(f"\n🔍 Проверка таблицы {table_name}...")
                
                try:
                    await cursor.execute(f"DESCRIBE {table_name}")
                    columns = await cursor.fetchall()
                    actual_cols = [col[0] for col in columns]
                    
                    missing_cols = set(expected_cols) - set(actual_cols)
                    extra_cols = set(actual_cols) - set(expected_cols)
                    
                    if missing_cols:
                        print(f"  ❌ Отсутствующие колонки: {list(missing_cols)}")
                        compatibility_issues.append(f"{table_name}: отсутствуют {list(missing_cols)}")
                    
                    if extra_cols:
                        print(f"  ℹ️ Дополнительные колонки: {list(extra_cols)}")
                    
                    if not missing_cols and not extra_cols:
                        print(f"  ✅ Структура соответствует ожидаемой")
                    elif not missing_cols:
                        print(f"  ⚠️ Структура совместима (есть дополнительные колонки)")
                    
                except Exception as e:
                    print(f"  ❌ Ошибка проверки: {e}")
                    compatibility_issues.append(f"{table_name}: ошибка проверки")
        
        connection.close()
        
        print(f"\n" + "=" * 60)
        if not compatibility_issues:
            print("✅ СТРУКТУРА ПОЛНОСТЬЮ СОВМЕСТИМА!")
            print("🚀 Можно приступать к созданию бота!")
        else:
            print("⚠️ НАЙДЕНЫ ПРОБЛЕМЫ СОВМЕСТИМОСТИ:")
            for issue in compatibility_issues:
                print(f"  • {issue}")
            print("\n💡 Нужно будет скорректировать структуру или код")
        
        return len(compatibility_issues) == 0
        
    except Exception as e:
        print(f"❌ Ошибка проверки совместимости: {e}")
        return False

async def main():
    print("🗄️ АНАЛИЗ СТРУКТУРЫ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Проверка структуры
    await check_table_structure()
    
    # Проверка совместимости
    compatible = await check_compatibility()
    
    if compatible:
        print(f"\n🎉 ГОТОВО К ИНТЕГРАЦИИ С БОТОМ!")
        print(f"Следующий шаг: создание файлов для бота")
    else:
        print(f"\n🔧 ТРЕБУЕТСЯ КОРРЕКТИРОВКА СТРУКТУРЫ")

if __name__ == "__main__":
    asyncio.run(main()) 