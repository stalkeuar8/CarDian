import pandas as pd
import re
import numpy as np

def process_car_data(cars_path, desc_path, output_path):
    print(f"--- Початок обробки ---")
    
    # 1. Завантаження даних
    try:
        # Вказуємо low_memory=False, щоб Pandas не скаржився на типи даних у великих файлах
        df_cars = pd.read_csv(cars_path, low_memory=False)
        df_desc = pd.read_csv(desc_path, low_memory=False)
    except Exception as e:
        print(f"Помилка при читанні файлів: {e}")
        return

    # Перевірка на збіг кількості рядків
    if len(df_cars) != len(df_desc):
        print(f"УВАГА: Кількість рядків різна! Cars: {len(df_cars)}, Desc: {len(df_desc)}")
        print("Переконайтеся, що рядки в обох файлах ідуть в одному порядку.")

    # 2. Функція витягування року з логічними фільтрами
    def extract_year_strict(text):
        if not isinstance(text, str) or pd.isna(text):
            return None
        
        # Шукаємо 4 цифри підряд. \b гарантує, що це окреме число.
        # Діапазон: 1980 - 2027 (актуально на квітень 2026 року)
        found = re.findall(r'\b(19[8-9][0-9]|20[0-2][0-9])\b', text)
        
        if not found:
            return None
        
        # Конвертуємо в int та фільтруємо аномалії (як 1916)
        valid_years = [int(y) for y in found if 1980 <= int(y) <= 2027]
        
        # Повертаємо перший знайдений адекватний рік
        return valid_years[0] if valid_years else None

    # 3. Підготовка колонки production_year
    # Перетворюємо існуючу колонку на числа, текст стає NaN
    df_cars['production_year'] = pd.to_numeric(df_cars['production_year'], errors='coerce')
    
    # Рахуємо скільки порожніх на старті
    initial_empty = df_cars['production_year'].isna().sum() + (df_cars['production_year'] == 0).sum()
    print(f"Порожніх або некоректних років на старті: {initial_empty}")

    # 4. Заповнення пропусків
    # Використовуємо маску для пошуку порожніх значень
    mask = (df_cars['production_year'].isna()) | (df_cars['production_year'] == 0)
    
    # Отримуємо масив описів (передбачається, що колонка називається 'description')
    # Якщо вона називається інакше, заміни 'description' на реальну назву
    if 'description' not in df_desc.columns:
        print("Помилка: У файлі descr.csv не знайдено колонку 'description'!")
        return

    desc_values = df_desc['description'].values
    
    print("Аналіз описів у процесі...")
    
    # Оновлюємо тільки порожні записи, використовуючи індекс для синхронізації
    indices_to_fix = df_cars[mask].index
    for idx in indices_to_fix:
        if idx < len(desc_values):
            found_year = extract_year_strict(desc_values[idx])
            if found_year:
                df_cars.at[idx, 'production_year'] = found_year

    # 5. Фінальна чистка аномалій
    # Видаляємо все, що виходить за межі 1980-2027 (якщо воно було там раніше)
    df_cars.loc[(df_cars['production_year'] < 1980) | (df_cars['production_year'] > 2027), 'production_year'] = 0
    
    # Заповнюємо NaN нулями та перетворюємо на Integer
    df_cars['production_year'] = df_cars['production_year'].fillna(0).astype(int)

    # 6. Статистика та збереження
    final_empty = (df_cars['production_year'] == 0).sum()
    recovered = initial_empty - final_empty
    
    print("-" * 30)
    print(f"ОБРОБКА ЗАВЕРШЕНА")
    print(f"Відновлено років з описів: {recovered}")
    print(f"Залишилося без року: {final_empty}")
    print("-" * 30)

    # Вивід топ-результатів для перевірки
    print("\nРозподіл по роках (Топ-5):")
    print(df_cars[df_cars['production_year'] > 0]['production_year'].value_counts().head())

    # Збереження
    df_cars.to_csv(output_path, index=False)
    print(f"\nФайл збережено: {output_path}")

# Виклик функції
process_car_data('cleaned_db.csv', 'descr.csv', 'final_cars_dataset.csv')