import customtkinter as ctk
from datetime import datetime, timedelta
import sqlite3
import json
import os
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from PIL import Image
import io

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CSTracker:
    def __init__(self):
        self.db_name = "cs_tracker.db"
        self.init_db()
        self.achievements = self.load_achievements()

        self.root = ctk.CTk()
        self.root.title("CS2 НАХуЙ ТИЛЬТ")
        self.root.geometry("1920x1200")

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Сегодня")
        self.tabview.add("Статистика")
        self.tabview.add("Достижения")
        self.tabview.add("История")

        self.setup_daily_tab()
        self.setup_stats_tab()
        self.setup_achievements_tab()
        self.setup_history_tab()

        self.load_today_data()

    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                dm_hours REAL DEFAULT 0,
                aim_trainer_hours REAL DEFAULT 0,
                matches_played INTEGER DEFAULT 0,
                matches_won INTEGER DEFAULT 0,
                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                headshot_percentage REAL DEFAULT 0,
                rating REAL DEFAULT 0,
                tilt_level INTEGER DEFAULT 0,
                focus_level INTEGER DEFAULT 0,
                notes TEXT,
                goals_tomorrow TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                achieved INTEGER DEFAULT 0,
                date_achieved TEXT,
                requirement_type TEXT,
                requirement_value REAL
            )
        ''')

        conn.commit()
        conn.close()

        self.init_achievements()

    def init_achievements(self):
        """Инициализация списка достижений"""
        achievements_data = [
            ("Первые 100 часов", "Провести 100 часов в тренировках", "total_hours", 100),
            ("Несгибаемый", "Тренироваться 30 дней подряд", "streak_days", 30),
            ("Снайпер", "Добиться 50% хедшотов", "headshot_percentage", 50),
            ("Хладнокровный", "Средний уровень тильта ниже 3", "avg_tilt", 3),
            ("Мастер ДМ", "100 часов в Deathmatch", "dm_hours", 100),
            ("Турнирный боец", "Сыграть 100 матчей", "total_matches", 100),
            ("Победитель", "Выиграть 50 матчей", "matches_won", 50),
            ("Без перерыва", "Тренироваться 7 дней подряд", "streak_days", 7),
            ("500 убийств", "Совершить 500 убийств", "total_kills", 500),
            ("Профессионал", "Достичь рейтинга 1.5", "avg_rating", 1.5),
        ]

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM achievements")
        if cursor.fetchone()[0] == 0:
            for name, desc, req_type, req_value in achievements_data:
                cursor.execute('''
                    INSERT INTO achievements (name, description, requirement_type, requirement_value)
                    VALUES (?, ?, ?, ?)
                ''', (name, desc, req_type, req_value))

        conn.commit()
        conn.close()

    def load_achievements(self) -> List[Dict]:
        """Загрузка достижений из БД"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM achievements")
        columns = [col[0] for col in cursor.description]
        achievements = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return achievements

    def setup_daily_tab(self):
        """Настройка вкладки для ежедневного заполнения"""
        tab = self.tabview.tab("Сегодня")

        self.date_label = ctk.CTkLabel(
            tab,
            text=f"Запись на {datetime.now().strftime('%d.%m.%Y')}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.date_label.pack(pady=10)

        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="both", expand=True, padx=20, pady=10)

        row = 0

        ctk.CTkLabel(input_frame, text="Часы в ДМ:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                             pady=10, sticky="w")
        self.dm_hours = ctk.CTkEntry(input_frame, width=100)
        self.dm_hours.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Часы с ботами:", font=ctk.CTkFont(size=14)).grid(row=row, column=0,
                                                                                              padx=10, pady=10,
                                                                                              sticky="w")
        self.aim_hours = ctk.CTkEntry(input_frame, width=100)
        self.aim_hours.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Сыграно матчей:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                          pady=10, sticky="w")
        self.matches_played = ctk.CTkEntry(input_frame, width=100)
        self.matches_played.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Выиграно матчей:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                           pady=10, sticky="w")
        self.matches_won = ctk.CTkEntry(input_frame, width=100)
        self.matches_won.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Убийств:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                           pady=10, sticky="w")
        self.kills = ctk.CTkEntry(input_frame, width=100)
        self.kills.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Смертей:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                            pady=10, sticky="w")
        self.deaths = ctk.CTkEntry(input_frame, width=100)
        self.deaths.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Процент хедшотов:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                            pady=10, sticky="w")
        self.hs_percent = ctk.CTkEntry(input_frame, width=100)
        self.hs_percent.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Личный рейтинг:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                          pady=10, sticky="w")
        self.rating = ctk.CTkEntry(input_frame, width=100)
        self.rating.grid(row=row, column=1, padx=10, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Уровень тильта (0-10):", font=ctk.CTkFont(size=14)).grid(row=row, column=0,
                                                                                                 padx=10, pady=10,
                                                                                                 sticky="w")
        self.tilt_level = ctk.CTkSlider(input_frame, from_=0, to=10, number_of_steps=10, width=200)
        self.tilt_level.grid(row=row, column=1, padx=10, pady=10)
        self.tilt_label = ctk.CTkLabel(input_frame, text="0")
        self.tilt_label.grid(row=row, column=2, padx=5, pady=10)
        row += 1

        ctk.CTkLabel(input_frame, text="Уровень фокуса (0-10):", font=ctk.CTkFont(size=14)).grid(row=row, column=0,
                                                                                                 padx=10, pady=10,
                                                                                                 sticky="w")
        self.focus_level = ctk.CTkSlider(input_frame, from_=0, to=10, number_of_steps=10, width=200)
        self.focus_level.grid(row=row, column=1, padx=10, pady=10)
        self.focus_label = ctk.CTkLabel(input_frame, text="0")
        self.focus_label.grid(row=row, column=2, padx=5, pady=10)
        row += 1

        self.tilt_level.configure(command=lambda v: self.tilt_label.configure(text=str(int(float(v)))))
        self.focus_level.configure(command=lambda v: self.focus_label.configure(text=str(int(float(v)))))

        ctk.CTkLabel(input_frame, text="Заметки за день:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                           pady=10, sticky="nw")
        self.notes = ctk.CTkTextbox(input_frame, width=300, height=100)
        self.notes.grid(row=row, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        row += 1

        ctk.CTkLabel(input_frame, text="Цели на завтра:", font=ctk.CTkFont(size=14)).grid(row=row, column=0, padx=10,
                                                                                          pady=10, sticky="nw")
        self.goals = ctk.CTkTextbox(input_frame, width=300, height=60)
        self.goals.grid(row=row, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Сохранить запись",
            command=self.save_daily_data,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            button_frame,
            text="Сбросить",
            command=self.reset_fields,
            font=ctk.CTkFont(size=14),
            width=150,
            height=40,
            fg_color="gray30"
        ).pack(side="left", padx=20)

    def setup_stats_tab(self):
        """Настройка вкладки статистики"""
        tab = self.tabview.tab("Статистика")

        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(control_frame, text="Период:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)

        self.period_var = ctk.StringVar(value="7")
        periods = [("7 дней", "7"), ("30 дней", "30"), ("90 дней", "90"), ("Все время", "all")]

        for text, value in periods:
            ctk.CTkRadioButton(control_frame, text=text, variable=self.period_var, value=value).pack(side="left",
                                                                                                     padx=5)

        ctk.CTkButton(control_frame, text="Обновить", command=self.update_stats).pack(side="right", padx=10)

        stats_frame = ctk.CTkFrame(tab)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = ctk.CTkFrame(stats_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.stats_labels = {}
        stats_to_show = [
            ("total_hours", "Всего часов:"),
            ("total_dm", "Часов в ДМ:"),
            ("avg_tilt", "Ср. уровень тильта:"),
            ("avg_focus", "Ср. уровень фокуса:"),
            ("total_matches", "Всего матчей:"),
            ("win_rate", "Процент побед:"),
            ("avg_kd", "Средний K/D:"),
            ("avg_hs", "Ср. % хедшотов:"),
            ("current_streak", "Текущая серия:"),
        ]

        for i, (key, text) in enumerate(stats_to_show):
            frame = ctk.CTkFrame(left_frame)
            frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=12)).pack(side="left")
            self.stats_labels[key] = ctk.CTkLabel(frame, text="0", font=ctk.CTkFont(size=14, weight="bold"))
            self.stats_labels[key].pack(side="right")

        right_frame = ctk.CTkFrame(stats_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def setup_achievements_tab(self):
        """Настройка вкладки достижений"""
        tab = self.tabview.tab("Достижения")

        scroll_frame = ctk.CTkScrollableFrame(tab, width=1100, height=600)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.achievement_frames = {}

        for i, achievement in enumerate(self.achievements):
            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(fill="x", padx=5, pady=5)

            if achievement['achieved']:
                frame.configure(fg_color=("#2e8b57", "#2e8b57"))  # Зеленый
            else:
                frame.configure(fg_color=("#3a3a3a", "#3a3a3a"))  # Серый

            name_label = ctk.CTkLabel(
                frame,
                text=achievement['name'],
                font=ctk.CTkFont(size=16, weight="bold")
            )
            name_label.pack(anchor="w", padx=10, pady=(10, 0))

            desc_label = ctk.CTkLabel(
                frame,
                text=achievement['description'],
                font=ctk.CTkFont(size=12)
            )
            desc_label.pack(anchor="w", padx=10)

            status_frame = ctk.CTkFrame(frame)
            status_frame.pack(anchor="w", padx=10, pady=(0, 10))

            if achievement['achieved']:
                status_text = f"Получено: {achievement['date_achieved']}"
            else:
                progress = self.calculate_achievement_progress(achievement)
                status_text = f"Прогресс: {progress}%"

            status_label = ctk.CTkLabel(
                status_frame,
                text=status_text,
                font=ctk.CTkFont(size=11)
            )
            status_label.pack(side="left", padx=5)

            self.achievement_frames[achievement['id']] = frame

    def setup_history_tab(self):
        """Настройка вкладки истории"""
        tab = self.tabview.tab("История")

        scroll_frame = ctk.CTkScrollableFrame(tab, width=1150, height=700)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        header_frame = ctk.CTkFrame(scroll_frame)
        header_frame.pack(fill="x", padx=5, pady=5)

        headers = ["Дата", "DM ч.", "Aim ч.", "Матчи", "Победы", "K/D", "HS%", "Тильт", "Фокус"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100 if i > 0 else 120
            )
            label.grid(row=0, column=i, padx=2, pady=2, sticky="ew")

        self.history_labels = []
        self.load_history(scroll_frame)

    def load_history(self, parent_frame):
        """Загрузка истории записей"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, dm_hours, aim_trainer_hours, matches_played, matches_won, 
                   kills, deaths, headshot_percentage, tilt_level, focus_level
            FROM daily_logs 
            ORDER BY date DESC
            LIMIT 50
        """)

        rows = cursor.fetchall()
        conn.close()

        for i, row in enumerate(rows, 1):
            frame = ctk.CTkFrame(parent_frame)
            frame.pack(fill="x", padx=5, pady=2)

            kd = "-"
            if row[5] is not None and row[6] is not None and row[6] > 0:
                kd = f"{row[5] / row[6]:.2f}"

            data = [
                row[0],  # Дата
                f"{row[1]:.1f}" if row[1] else "0",
                f"{row[2]:.1f}" if row[2] else "0",
                str(row[3]) if row[3] else "0",
                str(row[4]) if row[4] else "0",
                kd,
                f"{row[7]:.1f}%" if row[7] else "0%",
                str(int(row[8])) if row[8] is not None else "0",
                str(int(row[9])) if row[9] is not None else "0"
            ]

            if i % 2 == 0:
                frame.configure(fg_color=("#2d2d2d", "#2d2d2d"))

            for j, value in enumerate(data):
                label = ctk.CTkLabel(
                    frame,
                    text=value,
                    font=ctk.CTkFont(size=11),
                    width=100 if j > 0 else 120
                )
                label.grid(row=0, column=j, padx=2, pady=2, sticky="ew")

            self.history_labels.append(label)

    def load_today_data(self):
        """Загрузка данных за сегодня"""
        today = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_logs WHERE date = ?", (today,))
        data = cursor.fetchone()
        conn.close()

        if data:
            self.dm_hours.insert(0, str(data[2] or ""))
            self.aim_hours.insert(0, str(data[3] or ""))
            self.matches_played.insert(0, str(data[4] or ""))
            self.matches_won.insert(0, str(data[5] or ""))
            self.kills.insert(0, str(data[6] or ""))
            self.deaths.insert(0, str(data[7] or ""))
            self.hs_percent.insert(0, str(data[8] or ""))
            self.rating.insert(0, str(data[9] or ""))
            self.tilt_level.set(data[10] or 0)
            self.focus_level.set(data[11] or 0)
            self.notes.insert("1.0", data[12] or "")
            self.goals.insert("1.0", data[13] or "")

            self.tilt_label.configure(text=str(int(data[10] or 0)))
            self.focus_label.configure(text=str(int(data[11] or 0)))

    def save_daily_data(self):
        """Сохранение ежедневных данных"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            data = (
                today,
                float(self.dm_hours.get() or 0),
                float(self.aim_hours.get() or 0),
                int(self.matches_played.get() or 0),
                int(self.matches_won.get() or 0),
                int(self.kills.get() or 0),
                int(self.deaths.get() or 0),
                float(self.hs_percent.get() or 0),
                float(self.rating.get() or 0),
                int(self.tilt_level.get()),
                int(self.focus_level.get()),
                self.notes.get("1.0", "end-1c"),
                self.goals.get("1.0", "end-1c")
            )

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO daily_logs 
                (date, dm_hours, aim_trainer_hours, matches_played, matches_won, 
                 kills, deaths, headshot_percentage, rating, tilt_level, focus_level, notes, goals_tomorrow)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                dm_hours=excluded.dm_hours,
                aim_trainer_hours=excluded.aim_trainer_hours,
                matches_played=excluded.matches_played,
                matches_won=excluded.matches_won,
                kills=excluded.kills,
                deaths=excluded.deaths,
                headshot_percentage=excluded.headshot_percentage,
                rating=excluded.rating,
                tilt_level=excluded.tilt_level,
                focus_level=excluded.focus_level,
                notes=excluded.notes,
                goals_tomorrow=excluded.goals_tomorrow
            ''', data)

            conn.commit()
            conn.close()

            self.update_stats()
            self.check_achievements()

            self.show_notification("Данные сохранены!")

        except Exception as e:
            self.show_notification(f"Ошибка: {str(e)}")

    def reset_fields(self):
        """Сброс полей ввода"""
        self.dm_hours.delete(0, "end")
        self.aim_hours.delete(0, "end")
        self.matches_played.delete(0, "end")
        self.matches_won.delete(0, "end")
        self.kills.delete(0, "end")
        self.deaths.delete(0, "end")
        self.hs_percent.delete(0, "end")
        self.rating.delete(0, "end")
        self.tilt_level.set(0)
        self.focus_level.set(0)
        self.notes.delete("1.0", "end")
        self.goals.delete("1.0", "end")

        self.tilt_label.configure(text="0")
        self.focus_label.configure(text="0")

    def update_stats(self):
        """Обновление статистики"""
        period = self.period_var.get()

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if period == "all":
            date_filter = ""
            params = ()
        else:
            start_date = (datetime.now() - timedelta(days=int(period))).strftime("%Y-%m-%d")
            date_filter = "WHERE date >= ?"
            params = (start_date,)

        cursor.execute(f"""
            SELECT 
                COUNT(*) as days,
                SUM(dm_hours + aim_trainer_hours) as total_hours,
                SUM(dm_hours) as total_dm,
                AVG(tilt_level) as avg_tilt,
                AVG(focus_level) as avg_focus,
                SUM(matches_played) as total_matches,
                SUM(matches_won) as total_wins,
                SUM(kills) as total_kills,
                SUM(deaths) as total_deaths,
                AVG(headshot_percentage) as avg_hs
            FROM daily_logs
            {date_filter}
        """, params)

        stats = cursor.fetchone()

        days, total_hours, total_dm, avg_tilt, avg_focus, total_matches, total_wins, total_kills, total_deaths, avg_hs = stats

        win_rate = (total_wins / total_matches * 100) if total_matches > 0 else 0
        avg_kd = total_kills / total_deaths if total_deaths > 0 else 0

        cursor.execute("""
            WITH RECURSIVE dates AS (
                SELECT date(date) as date
                FROM daily_logs
                WHERE (dm_hours + aim_trainer_hours) > 0
                ORDER BY date DESC
            ),
            streaks AS (
                SELECT date,
                       julianday(date) - julianday(LAG(date, 1, date) OVER (ORDER BY date DESC)) as diff
                FROM dates
            )
            SELECT COUNT(*) as streak
            FROM streaks
            WHERE diff = 1 OR diff IS NULL
            LIMIT 1
        """)

        current_streak = cursor.fetchone()[0] or 0

        conn.close()

        self.stats_labels['total_hours'].configure(text=f"{total_hours or 0:.1f} ч.")
        self.stats_labels['total_dm'].configure(text=f"{total_dm or 0:.1f} ч.")
        self.stats_labels['avg_tilt'].configure(text=f"{avg_tilt or 0:.1f}/10")
        self.stats_labels['avg_focus'].configure(text=f"{avg_focus or 0:.1f}/10")
        self.stats_labels['total_matches'].configure(text=str(total_matches or 0))
        self.stats_labels['win_rate'].configure(text=f"{win_rate:.1f}%")
        self.stats_labels['avg_kd'].configure(text=f"{avg_kd:.2f}")
        self.stats_labels['avg_hs'].configure(text=f"{avg_hs or 0:.1f}%")
        self.stats_labels['current_streak'].configure(text=f"{current_streak} дней")

        self.update_chart(period)

    def update_chart(self, period):
        """Обновление графика"""
        self.ax.clear()

        conn = sqlite3.connect(self.db_name)

        if period == "all":
            query = """
                SELECT date, (dm_hours + aim_trainer_hours) as hours, tilt_level, focus_level
                FROM daily_logs 
                ORDER BY date
            """
            df = pd.read_sql_query(query, conn)
        else:
            start_date = (datetime.now() - timedelta(days=int(period))).strftime("%Y-%m-%d")
            query = """
                SELECT date, (dm_hours + aim_trainer_hours) as hours, tilt_level, focus_level
                FROM daily_logs 
                WHERE date >= ?
                ORDER BY date
            """
            df = pd.read_sql_query(query, conn, params=(start_date,))

        conn.close()

        if len(df) > 0:
            df['date'] = pd.to_datetime(df['date'])

            self.ax.bar(df['date'], df['hours'], color='skyblue', alpha=0.7, label='Часы тренировок')
            self.ax.set_ylabel('Часы', color='skyblue')
            self.ax.tick_params(axis='y', labelcolor='skyblue')

            ax2 = self.ax.twinx()
            ax2.plot(df['date'], df['tilt_level'], 'r-', label='Тильт', linewidth=2)
            ax2.plot(df['date'], df['focus_level'], 'g-', label='Фокус', linewidth=2)
            ax2.set_ylabel('Уровень (0-10)', color='black')
            ax2.tick_params(axis='y', labelcolor='black')
            ax2.set_ylim(0, 10)

            self.ax.set_xlabel('Дата')
            self.ax.set_title('Прогресс тренировок')
            self.ax.legend(loc='upper left')
            ax2.legend(loc='upper right')

            plt.xticks(rotation=45)
            plt.tight_layout()

        self.canvas.draw()

    def check_achievements(self):
        """Проверка и обновление достижений"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                SUM(dm_hours + aim_trainer_hours) as total_hours,
                SUM(dm_hours) as dm_hours,
                AVG(tilt_level) as avg_tilt,
                SUM(matches_played) as total_matches,
                SUM(matches_won) as matches_won,
                SUM(kills) as total_kills,
                AVG((kills*1.0)/NULLIF(deaths, 0)) as avg_rating
            FROM daily_logs
        """)

        stats = cursor.fetchone()
        total_hours, dm_hours, avg_tilt, total_matches, matches_won, total_kills, avg_rating = stats

        cursor.execute("""
            WITH RECURSIVE dates AS (
                SELECT date(date) as date
                FROM daily_logs
                WHERE (dm_hours + aim_trainer_hours) > 0
                ORDER BY date DESC
            ),
            streaks AS (
                SELECT date,
                       julianday(date) - julianday(LAG(date, 1, date) OVER (ORDER BY date DESC)) as diff
                FROM dates
            )
            SELECT COUNT(*) as streak
            FROM streaks
            WHERE diff = 1 OR diff IS NULL
            LIMIT 1
        """)

        streak_days = cursor.fetchone()[0] or 0

        cursor.execute("SELECT * FROM achievements WHERE achieved = 0")
        achievements = cursor.fetchall()

        today = datetime.now().strftime("%Y-%m-%d")

        for ach in achievements:
            ach_id, name, desc, achieved, date_achieved, req_type, req_value = ach

            progress = 0
            is_achieved = False

            if req_type == "total_hours" and total_hours:
                progress = min(100, (total_hours / req_value) * 100)
                is_achieved = total_hours >= req_value
            elif req_type == "streak_days" and streak_days:
                progress = min(100, (streak_days / req_value) * 100)
                is_achieved = streak_days >= req_value
            elif req_type == "dm_hours" and dm_hours:
                progress = min(100, (dm_hours / req_value) * 100)
                is_achieved = dm_hours >= req_value
            elif req_type == "avg_tilt" and avg_tilt:
                progress = min(100, max(0, (1 - avg_tilt / 10) * 100))
                is_achieved = avg_tilt <= req_value
            elif req_type == "total_matches" and total_matches:
                progress = min(100, (total_matches / req_value) * 100)
                is_achieved = total_matches >= req_value
            elif req_type == "matches_won" and matches_won:
                progress = min(100, (matches_won / req_value) * 100)
                is_achieved = matches_won >= req_value
            elif req_type == "total_kills" and total_kills:
                progress = min(100, (total_kills / req_value) * 100)
                is_achieved = total_kills >= req_value
            elif req_type == "avg_rating" and avg_rating:
                progress = min(100, (avg_rating / req_value) * 100)
                is_achieved = avg_rating >= req_value

            if is_achieved and not achieved:
                cursor.execute(
                    "UPDATE achievements SET achieved = 1, date_achieved = ? WHERE id = ?",
                    (today, ach_id)
                )

        conn.commit()
        conn.close()

        self.achievements = self.load_achievements()
        self.refresh_achievements_tab()

    def calculate_achievement_progress(self, achievement):
        """Расчет прогресса достижения"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                SUM(dm_hours + aim_trainer_hours) as total_hours,
                SUM(dm_hours) as dm_hours,
                AVG(tilt_level) as avg_tilt,
                SUM(matches_played) as total_matches,
                SUM(matches_won) as matches_won,
                SUM(kills) as total_kills
            FROM daily_logs
        """)

        stats = cursor.fetchone()
        conn.close()

        total_hours, dm_hours, avg_tilt, total_matches, matches_won, total_kills = stats

        req_type = achievement['requirement_type']
        req_value = achievement['requirement_value']

        progress = 0

        if req_type == "total_hours" and total_hours:
            progress = min(100, (total_hours / req_value) * 100)
        elif req_type == "dm_hours" and dm_hours:
            progress = min(100, (dm_hours / req_value) * 100)
        elif req_type == "avg_tilt" and avg_tilt:
            progress = min(100, max(0, (1 - avg_tilt / 10) * 100))
        elif req_type == "total_matches" and total_matches:
            progress = min(100, (total_matches / req_value) * 100)
        elif req_type == "matches_won" and matches_won:
            progress = min(100, (matches_won / req_value) * 100)
        elif req_type == "total_kills" and total_kills:
            progress = min(100, (total_kills / req_value) * 100)

        return int(progress)

    def refresh_achievements_tab(self):
        """Обновление вкладки достижений"""
        tab = self.tabview.tab("Достижения")
        for widget in tab.winfo_children():
            widget.destroy()

        self.setup_achievements_tab()

    def show_notification(self, message):
        """Показать уведомление"""
        notification = ctk.CTkToplevel(self.root)
        notification.title("Уведомление")
        notification.geometry("300x100")
        notification.transient(self.root)
        notification.grab_set()

        notification.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (300 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (100 // 2)
        notification.geometry(f"+{x}+{y}")

        ctk.CTkLabel(notification, text=message, font=ctk.CTkFont(size=14)).pack(expand=True)

        notification.after(2000, notification.destroy)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CSTracker()
    app.run()