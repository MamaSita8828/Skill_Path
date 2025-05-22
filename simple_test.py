import asyncio
import aiomysql

async def test_connection():
    print("🔄 Проверка подключения к MySQL...")
    
    try:
        connection = await aiomysql.connect(
            host='turntable.proxy.rlwy.net',
            port=11725,
            user='root',
            password='obyRyMEAMtDgJsSxGkontTXPZzwJdtFR',
            db='railway',
            charset='utf8mb4'
        )
        
        print("✅ Подключение успешно!")
        
        # Проверяем базу данных
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT DATABASE()")
            db_name = await cursor.fetchone()
            print(f"📊 База данных: {db_name[0]}")
            
            # Проверяем таблицы
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            print(f"📋 Таблиц в базе: {len(tables)}")
            
            if tables:
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("  Таблицы не найдены")
        
        connection.close()
        print("✅ Тест завершен успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection()) 