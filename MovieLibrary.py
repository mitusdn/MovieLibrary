import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ========== Конфигурация ==========
DATA_FILE = "movies.json"

# Список жанров
GENRES = [
    "Боевик", "Комедия", "Драма", "Фантастика", "Ужасы",
    "Триллер", "Мелодрама", "Детектив", "Приключения", "Анимация",
    "Документальный", "Криминал", "Семейный", "Фэнтези", "Вестерн"
]

# ========== Работа с файлом ==========
def load_movies():
    """Загружает фильмы из JSON файла"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_movies(movies):
    """Сохраняет фильмы в JSON файл"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(movies, file, ensure_ascii=False, indent=4)
    except IOError:
        messagebox.showerror("Ошибка", "Не удалось сохранить данные!")

def add_movie():
    """Добавляет новый фильм"""
    # Получаем данные из полей ввода
    title = title_entry.get().strip()
    genre = genre_var.get()
    year = year_entry.get().strip()
    rating = rating_entry.get().strip()
    
    # Валидация данных
    if not title:
        messagebox.showwarning("Предупреждение", "Введите название фильма!")
        return
    
    if not genre:
        messagebox.showwarning("Предупреждение", "Выберите жанр фильма!")
        return
    
    if not year:
        messagebox.showwarning("Предупреждение", "Введите год выпуска!")
        return
    
    if not rating:
        messagebox.showwarning("Предупреждение", "Введите рейтинг фильма!")
        return
    
    # Проверка года
    try:
        year_int = int(year)
        current_year = datetime.now().year
        if year_int < 1888 or year_int > current_year:
            messagebox.showwarning("Предупреждение", f"Год должен быть от 1888 до {current_year}!")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Год должен быть целым числом!")
        return
    
    # Проверка рейтинга
    try:
        rating_float = float(rating)
        if rating_float < 0 or rating_float > 10:
            messagebox.showwarning("Предупреждение", "Рейтинг должен быть от 0 до 10!")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
        return
    
    # Создаём запись
    movie = {
        "title": title,
        "genre": genre,
        "year": year_int,
        "rating": rating_float,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Добавляем в список
    movies.append(movie)
    save_movies(movies)
    
    # Очищаем поля
    title_entry.delete(0, tk.END)
    genre_var.set("")
    year_entry.delete(0, tk.END)
    rating_entry.delete(0, tk.END)
    
    # Обновляем отображение
    update_table(movies)
    update_stats()
    
    messagebox.showinfo("Успех", f"Фильм '{title}' добавлен в библиотеку!")

def delete_movie():
    """Удаляет выбранный фильм"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Предупреждение", "Выберите фильм для удаления!")
        return
    
    if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот фильм?"):
        for item in selected:
            item_values = tree.item(item, "values")
            # Удаляем из списка
            for i, movie in enumerate(movies):
                if (movie["title"] == item_values[0] and 
                    movie["genre"] == item_values[1] and
                    movie["year"] == int(item_values[2]) and
                    movie["rating"] == float(item_values[3])):
                    movies.pop(i)
                    break
        
        save_movies(movies)
        update_table(movies)
        update_stats()
        messagebox.showinfo("Успех", "Фильм удалён!")

def filter_movies():
    """Фильтрует фильмы по жанру и году"""
    filtered = movies.copy()
    
    # Фильтр по жанру
    genre_filter = filter_genre_var.get()
    if genre_filter != "Все жанры":
        filtered = [m for m in filtered if m["genre"] == genre_filter]
    
    # Фильтр по году
    year_filter = filter_year_entry.get().strip()
    if year_filter:
        try:
            year_int = int(year_filter)
            filtered = [m for m in filtered if m["year"] == year_int]
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат года фильтрации!")
            return
    
    update_table(filtered)
    update_filtered_stats(filtered)
    
    filter_label.config(
        text=f"🔍 Найдено фильмов: {len(filtered)}",
        fg="green"
    )

def reset_filters():
    """Сбрасывает фильтры"""
    filter_genre_var.set("Все жанры")
    filter_year_entry.delete(0, tk.END)
    filter_label.config(text="")
    update_table(movies)
    update_filtered_stats(movies)

def update_table(movies_to_show):
    """Обновляет таблицу с фильмами"""
    # Очищаем таблицу
    for row in tree.get_children():
        tree.delete(row)
    
    # Добавляем записи
    total_rating = 0
    for movie in movies_to_show:
        # Звёздочки для рейтинга
        stars = "⭐" * int(movie["rating"] // 2) + "☆" * (5 - int(movie["rating"] // 2))
        
        tree.insert("", "end", values=(
            movie["title"],
            movie["genre"],
            movie["year"],
            f"{movie['rating']:.1f}",
            stars
        ))
        total_rating += movie["rating"]
    
    # Обновляем общую статистику
    if movies_to_show:
        avg_rating = total_rating / len(movies_to_show)
        total_label.config(
            text=f"🎬 Всего фильмов: {len(movies_to_show)} | Средний рейтинг: {avg_rating:.1f}",
            fg="#333333"
        )
    else:
        total_label.config(text="🎬 Всего фильмов: 0 | Средний рейтинг: 0", fg="#333333")

def update_stats():
    """Обновляет общую статистику"""
    update_table(movies)

def update_filtered_stats(filtered_movies):
    """Обновляет статистику для отфильтрованных данных"""
    if filtered_movies:
        total_rating = sum(m["rating"] for m in filtered_movies)
        avg_rating = total_rating / len(filtered_movies)
        filter_total_label.config(text=f"📊 Средний рейтинг фильтра: {avg_rating:.1f}")
    else:
        filter_total_label.config(text="📊 Средний рейтинг фильтра: 0")

def show_movie_stats():
    """Показывает подробную статистику фильмов"""
    if not movies:
        messagebox.showinfo("Информация", "Нет фильмов для статистики!")
        return
    
    stats_window = tk.Toplevel(root)
    stats_window.title("Статистика фильмов")
    stats_window.geometry("600x500")
    stats_window.configure(bg="#f5f5f5")
    stats_window.resizable(False, False)
    
    tk.Label(
        stats_window,
        text="🎬 Статистика фильмотеки 🎬",
        font=("Arial", 14, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(pady=15)
    
    # Общая статистика
    total_movies = len(movies)
    total_rating = sum(m["rating"] for m in movies)
    avg_rating = total_rating / total_movies if total_movies > 0 else 0
    years = [m["year"] for m in movies]
    oldest = min(years) if years else 0
    newest = max(years) if years else 0
    
    stats_frame = tk.Frame(stats_window, bg="#f5f5f5")
    stats_frame.pack(pady=10, padx=20, fill="x")
    
    stats = [
        ("Всего фильмов:", f"{total_movies}"),
        ("Средний рейтинг:", f"{avg_rating:.1f} / 10"),
        ("Самый старый фильм:", f"{oldest} год"),
        ("Самый новый фильм:", f"{newest} год")
    ]
    
    for i, (label, value) in enumerate(stats):
        tk.Label(stats_frame, text=label, font=("Arial", 11, "bold"), bg="#f5f5f5").grid(row=i, column=0, sticky="w", pady=5, padx=10)
        tk.Label(stats_frame, text=value, font=("Arial", 11), bg="#f5f5f5", fg="#4CAF50").grid(row=i, column=1, sticky="w", pady=5, padx=10)
    
    # Статистика по жанрам
    tk.Label(
        stats_window,
        text="Статистика по жанрам:",
        font=("Arial", 11, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(pady=(20, 10))
    
    genre_stats_frame = tk.Frame(stats_window, bg="#f5f5f5")
    genre_stats_frame.pack(pady=5, padx=20, fill="both", expand=True)
    
    # Собираем статистику по жанрам
    genre_counts = {}
    genre_ratings = {}
    for movie in movies:
        genre = movie["genre"]
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        genre_ratings[genre] = genre_ratings.get(genre, 0) + movie["rating"]
    
    # Создаём таблицу для статистики по жанрам
    columns = ("Жанр", "Количество", "Средний рейтинг")
    stats_tree = ttk.Treeview(genre_stats_frame, columns=columns, show="headings", height=10)
    
    stats_tree.heading("Жанр", text="Жанр")
    stats_tree.heading("Количество", text="Количество фильмов")
    stats_tree.heading("Средний рейтинг", text="Средний рейтинг")
    
    stats_tree.column("Жанр", width=150)
    stats_tree.column("Количество", width=120)
    stats_tree.column("Средний рейтинг", width=120)
    
    for genre in sorted(genre_counts.keys()):
        avg = genre_ratings[genre] / genre_counts[genre]
        stats_tree.insert("", "end", values=(
            genre,
            genre_counts[genre],
            f"{avg:.1f}"
        ))
    
    stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    scrollbar = ttk.Scrollbar(genre_stats_frame, orient=tk.VERTICAL, command=stats_tree.yview)
    stats_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

def show_top_rated():
    """Показывает топ-5 лучших фильмов"""
    if not movies:
        messagebox.showinfo("Информация", "Нет фильмов для отображения!")
        return
    
    sorted_movies = sorted(movies, key=lambda x: x["rating"], reverse=True)
    top_movies = sorted_movies[:5]
    
    top_window = tk.Toplevel(root)
    top_window.title("Топ-5 лучших фильмов")
    top_window.geometry("500x400")
    top_window.configure(bg="#f5f5f5")
    top_window.resizable(False, False)
    
    tk.Label(
        top_window,
        text="⭐ Топ-5 лучших фильмов ⭐",
        font=("Arial", 14, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(pady=15)
    
    # Создаём таблицу
    columns = ("Название", "Жанр", "Год", "Рейтинг")
    top_tree = ttk.Treeview(top_window, columns=columns, show="headings", height=5)
    
    top_tree.heading("Название", text="Название")
    top_tree.heading("Жанр", text="Жанр")
    top_tree.heading("Год", text="Год")
    top_tree.heading("Рейтинг", text="Рейтинг")
    
    top_tree.column("Название", width=200)
    top_tree.column("Жанр", width=100)
    top_tree.column("Год", width=80)
    top_tree.column("Рейтинг", width=80)
    
    for i, movie in enumerate(top_movies, 1):
        top_tree.insert("", "end", values=(
            f"{i}. {movie['title']}",
            movie["genre"],
            movie["year"],
            f"{movie['rating']:.1f}"
        ))
    
    top_tree.pack(pady=10, padx=20, fill="both", expand=True)

def export_to_csv():
    """Экспортирует фильмы в CSV файл"""
    if not movies:
        messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
        return
    
    try:
        with open("movies_export.csv", "w", encoding="utf-8") as file:
            file.write("Название,Жанр,Год,Рейтинг,Дата добавления\n")
            for movie in movies:
                file.write(f"\"{movie['title']}\",{movie['genre']},{movie['year']},{movie['rating']},\"{movie.get('added_date', '')}\"\n")
        
        messagebox.showinfo("Успех", "Данные экспортированы в файл movies_export.csv!")
    except IOError:
        messagebox.showerror("Ошибка", "Не удалось экспортировать данные!")

# ========== Создание GUI ==========
root = tk.Tk()
root.title("Movie Library - Библиотека фильмов")
root.geometry("1100x700")
root.resizable(False, False)
root.configure(bg="#f5f5f5")

# Загрузка данных
movies = load_movies()

# ========== Верхняя панель (заголовок) ==========
title_label = tk.Label(
    root,
    text="🎬 Movie Library - Библиотека фильмов 🎬",
    font=("Arial", 18, "bold"),
    bg="#f5f5f5",
    fg="#333333"
)
title_label.pack(pady=15)

subtitle_label = tk.Label(
    root,
    text="Храни информацию о любимых фильмах, оценивай и открывай новые!",
    font=("Arial", 10),
    bg="#f5f5f5",
    fg="#666666"
)
subtitle_label.pack(pady=(0, 15))

# ========== Форма добавления фильма ==========
form_frame = tk.LabelFrame(root, text="➕ Добавить фильм", font=("Arial", 12, "bold"), bg="#f5f5f5")
form_frame.pack(pady=10, padx=20, fill="x")

# Название
tk.Label(form_frame, text="Название:", font=("Arial", 10), bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=10, sticky="w")
title_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
title_entry.grid(row=0, column=1, padx=10, pady=10)

# Жанр
tk.Label(form_frame, text="Жанр:", font=("Arial", 10), bg="#f5f5f5").grid(row=0, column=2, padx=10, pady=10, sticky="w")
genre_var = tk.StringVar()
genre_combo = ttk.Combobox(form_frame, textvariable=genre_var, values=GENRES, state="readonly", width=15)
genre_combo.grid(row=0, column=3, padx=10, pady=10)

# Год выпуска
tk.Label(form_frame, text="Год выпуска:", font=("Arial", 10), bg="#f5f5f5").grid(row=0, column=4, padx=10, pady=10, sticky="w")
year_entry = tk.Entry(form_frame, width=10, font=("Arial", 10))
year_entry.grid(row=0, column=5, padx=10, pady=10)

# Рейтинг
tk.Label(form_frame, text="Рейтинг (0-10):", font=("Arial", 10), bg="#f5f5f5").grid(row=0, column=6, padx=10, pady=10, sticky="w")
rating_entry = tk.Entry(form_frame, width=8, font=("Arial", 10))
rating_entry.grid(row=0, column=7, padx=10, pady=10)

# Кнопка добавления
add_button = tk.Button(
    form_frame,
    text="➕ Добавить фильм",
    command=add_movie,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    cursor="hand2"
)
add_button.grid(row=1, column=0, columnspan=8, pady=10)

# ========== Панель фильтрации ==========
filter_frame = tk.LabelFrame(root, text="🔍 Фильтрация фильмов", font=("Arial", 12, "bold"), bg="#f5f5f5")
filter_frame.pack(pady=10, padx=20, fill="x")

# Фильтр по жанру
tk.Label(filter_frame, text="Жанр:", font=("Arial", 10), bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=10, sticky="w")
filter_genre_var = tk.StringVar(value="Все жанры")
filter_genre_combo = ttk.Combobox(filter_frame, textvariable=filter_genre_var, values=["Все жанры"] + GENRES, state="readonly", width=15)
filter_genre_combo.grid(row=0, column=1, padx=10, pady=10)

# Фильтр по году
tk.Label(filter_frame, text="Год выпуска:", font=("Arial", 10), bg="#f5f5f5").grid(row=0, column=2, padx=10, pady=10, sticky="w")
filter_year_entry = tk.Entry(filter_frame, width=10, font=("Arial", 10))
filter_year_entry.grid(row=0, column=3, padx=10, pady=10)

# Кнопки фильтрации
filter_button = tk.Button(
    filter_frame,
    text="🔍 Применить фильтр",
    command=filter_movies,
    bg="#2196F3",
    fg="white",
    cursor="hand2"
)
filter_button.grid(row=0, column=4, padx=5, pady=10)

reset_filter_button = tk.Button(
    filter_frame,
    text="🔄 Сбросить фильтр",
    command=reset_filters,
    bg="#9E9E9E",
    fg="white",
    cursor="hand2"
)
reset_filter_button.grid(row=0, column=5, padx=5, pady=10)

# Метка статуса фильтра
filter_label = tk.Label(filter_frame, text="", font=("Arial", 9), bg="#f5f5f5")
filter_label.grid(row=1, column=0, columnspan=6, pady=5)

# ========== Таблица фильмов ==========
table_frame = tk.LabelFrame(root, text="📋 Мои фильмы", font=("Arial", 12, "bold"), bg="#f5f5f5")
table_frame.pack(pady=10, padx=20, fill="both", expand=True)

# Создаём таблицу
columns = ("Название", "Жанр", "Год", "Рейтинг", "")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

tree.heading("Название", text="Название")
tree.heading("Жанр", text="Жанр")
tree.heading("Год", text="Год")
tree.heading("Рейтинг", text="Рейтинг")
tree.heading("", text="")

tree.column("Название", width=250)
tree.column("Жанр", width=120)
tree.column("Год", width=80)
tree.column("Рейтинг", width=80)
tree.column("", width=200)

# Скроллбар
scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

# ========== Нижняя панель ==========
bottom_frame = tk.Frame(root, bg="#f5f5f5")
bottom_frame.pack(pady=10, padx=20, fill="x")

# Кнопка удаления
delete_button = tk.Button(
    bottom_frame,
    text="🗑 Удалить выбранный фильм",
    command=delete_movie,
    bg="#f44336",
    fg="white",
    font=("Arial", 10, "bold"),
    cursor="hand2"
)
delete_button.pack(side=tk.LEFT, padx=5)

# Кнопка статистики
stats_button = tk.Button(
    bottom_frame,
    text="📊 Статистика",
    command=show_movie_stats,
    bg="#FF9800",
    fg="white",
    font=("Arial", 10, "bold"),
    cursor="hand2"
)
stats_button.pack(side=tk.LEFT, padx=5)

# Кнопка топ фильмов
top_button = tk.Button(
    bottom_frame,
    text="⭐ Топ-5 фильмов",
    command=show_top_rated,
    bg="#9C27B0",
    fg="white",
    font=("Arial", 10, "bold"),
    cursor="hand2"
)
top_button.pack(side=tk.LEFT, padx=5)

# Кнопка экспорта
export_button = tk.Button(
    bottom_frame,
    text="📁 Экспорт в CSV",
    command=export_to_csv,
    bg="#00BCD4",
    fg="white",
    font=("Arial", 10, "bold"),
    cursor="hand2"
)
export_button.pack(side=tk.LEFT, padx=5)

# Общая статистика
total_label = tk.Label(
    bottom_frame,
    text="🎬 Всего фильмов: 0 | Средний рейтинг: 0",
    font=("Arial", 10, "bold"),
    bg="#f5f5f5",
    fg="#333333"
)
total_label.pack(side=tk.RIGHT, padx=5)

# Статистика фильтра
filter_total_label = tk.Label(
    bottom_frame,
    text="",
    font=("Arial", 9),
    bg="#f5f5f5",
    fg="#666666"
)
filter_total_label.pack(side=tk.RIGHT, padx=5)

# Информационная метка
info_label = tk.Label(
    root,
    text="💡 Совет: Нажмите Enter для быстрого добавления. Рейтинг отображается звёздочками (⭐ = 2 балла)!",
    font=("Arial", 8),
    bg="#f5f5f5",
    fg="#888888"
)
info_label.pack(side="bottom", pady=5)

# Привязываем Enter
title_entry.bind("<Return>", lambda event: add_movie())
year_entry.bind("<Return>", lambda event: add_movie())
rating_entry.bind("<Return>", lambda event: add_movie())

# Заполняем таблицу
update_table(movies)

# Запуск приложения
root.mainloop()