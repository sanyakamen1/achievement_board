import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="Achievements", layout="wide")
st.title("🏆 Achievements")

BASE_DIR = Path(__file__).parent
GRAY_IMG = BASE_DIR / "images" / "gray.png"
GOLD_IMG = BASE_DIR / "images" / "gold.png"
DATA_FILE = BASE_DIR / "data.json"

# --- Загрузка прогресса ---
if DATA_FILE.exists():
    with open(DATA_FILE, "r") as f:
        achievements = json.load(f)
else:
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

# --- Функция для обработки клика ---
def toggle_achievement(name):
    if not st.session_state[name]:
        st.session_state[name] = True
        st.toast(f"🏆 Achievement unlocked: {name}")

# --- Рендер медалей ---
cols_per_row = 3
col_index = 0
cols = st.columns(cols_per_row)

for name in achievements.keys():
    col = cols[col_index]
    with col:
        st.checkbox(
            name,
            value=st.session_state[name],
            key=name,
            on_change=toggle_achievement,
            args=(name,)
        )
        st.image(str(GOLD_IMG) if st.session_state[name] else str(GRAY_IMG), width=64)

    col_index += 1
    if col_index >= cols_per_row:
        col_index = 0
        cols = st.columns(cols_per_row)

# --- Сохранение прогресса ---
for name in achievements.keys():
    achievements[name] = st.session_state[name]

with open(DATA_FILE, "w") as f:
    json.dump(achievements, f, indent=2)
