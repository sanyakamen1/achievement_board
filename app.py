import streamlit as st
from pathlib import Path
import json

# --- Настройки страницы ---
st.set_page_config(page_title="Achievements", layout="wide")
st.title("🏆 Achievement Board")

# --- Пути к картинкам ---
BASE_DIR = Path(__file__).parent
GRAY_IMG = BASE_DIR / "images" / "gray.png"
GOLD_IMG = BASE_DIR / "images" / "gold.png"

# --- Файл для хранения прогресса ---
DATA_FILE = BASE_DIR / "data.json"

# --- Загрузка прогресса ---
if DATA_FILE.exists():
    with open(DATA_FILE, "r") as f:
        achievements = json.load(f)
else:
    # начальные достижения
    achievements = {
        "Run 10 km": False,
        "Read 5 books": False,
        "Meditate 7 days": False,
        "Write 1000 words": False,
        "Learn Python basics": False
    }

# --- Инициализация session_state ---
for name, done in achievements.items():
    if name not in st.session_state:
        st.session_state[name] = done
    # флаг для toast
    toast_key = f"{name}_toast_shown"
    if toast_key not in st.session_state:
        st.session_state[toast_key] = done  # если уже выполнено, toast не показывать

# --- Функция обработки изменения чекбокса ---
def on_checkbox_change(name):
    """Показывает toast один раз при первом открытии достижения"""
    new_value = st.session_state[name]
    toast_key = f"{name}_toast_shown"

    if new_value and not st.session_state[toast_key]:
        st.toast(f"🏆 Achievement unlocked: {name}")
        st.session_state[toast_key] = True

# --- Рендер сетки медалей ---
cols_per_row = 3
col_index = 0
cols = st.columns(cols_per_row)

for name in achievements.keys():
    col = cols[col_index]
    with col:
        # Чекбокс с on_change
        st.checkbox(
            label=name,
            key=name,
            on_change=on_checkbox_change,
            args=(name,)
        )
        # Медалька
        st.image(str(GOLD_IMG) if st.session_state[name] else str(GRAY_IMG), width=64)

    col_index += 1
    if col_index >= cols_per_row:
        col_index = 0
        cols = st.columns(cols_per_row)

# --- Сохранение прогресса в JSON ---
for name in achievements.keys():
    achievements[name] = st.session_state[name]

with open(DATA_FILE, "w") as f:
    json.dump(achievements, f, indent=2)