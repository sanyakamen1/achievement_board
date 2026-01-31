import streamlit as st
import json
from pathlib import Path

DATA_FILE = Path("data.json")
GRAY_IMG = "images/gray.png"
GOLD_IMG = "images/gold.png"

st.set_page_config(page_title="Achievements", layout="wide")
st.title("🏆 Achievements")

# --- Загрузка данных ---
if DATA_FILE.exists():
    with open(DATA_FILE, "r") as f:
        achievements = json.load(f)
else:
    achievements = {}

# --- UI ---
cols = st.columns(3)  # три медали в ряд
col_index = 0

for name, done in achievements.items():
    col = cols[col_index]
    with col:
        st.image(GOLD_IMG if done else GRAY_IMG, width=64)
        checked = st.checkbox(name, value=done, key=name)
        if checked and not done:
            st.toast(f"🏆 Achievement unlocked: {name}")
            achievements[name] = True
        elif not checked and done:
            achievements[name] = False  # если снимаем галочку

    col_index += 1
    if col_index >= len(cols):
        col_index = 0
        cols = st.columns(3)  # новая строка

# --- Сохранение прогресса ---
with open(DATA_FILE, "w") as f:
    json.dump(achievements, f, indent=2)