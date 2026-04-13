import sqlite3
import pandas as pd

def export_db_to_csv(db_path, csv_path):
    try:
        # 1. Підключаємося до бази
        conn = sqlite3.connect(db_path)
        
        # 2. Дізнаємося назву таблиці (вона там зазвичай одна)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_name = cursor.fetchone()[0]
        print(f"📦 Знайдено таблицю: {table_name}")

        # 3. Витягуємо всі дані через Pandas
        print("⏳ Читання даних з бази...")
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        
        # 4. Зберігаємо в CSV
        print(f"💾 Збереження у {csv_path}...")
        df.to_csv(csv_path, index=False)
        
        conn.close()
        print("✅ Готово! Дані перенесено без втрат.")

    except Exception as e:
        print(f"❌ Помилка: {e}")
        print("\nЯкщо пише 'file is not a database', спробуй просто перейменувати файл вручну в .csv — можливо, ти зберіг текст з неправильним розширенням.")

# Запуск
export_db_to_csv('autoscout_dataset.db', 'dataset.csv')