import streamlit as st
from pathlib import Path
import json
import base64

st.set_page_config(page_title="Achievements", layout="wide")
st.title("🏆 Achievement Board")

BASE_DIR = Path(__file__).parent
GRAY_IMG = BASE_DIR / "images/gray.png"
GOLD_IMG = BASE_DIR / "images/gold.png"
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
    toast_key = f"{name}_toast_shown"
    if toast_key not in st.session_state:
        st.session_state[toast_key] = done

# --- Вспомогательная функция: конвертирует картинку в Base64 ---
def img_to_base64(path: Path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- Функция при клике на чекбокс ---
def on_checkbox_change(name):
    new_value = st.session_state[name]
    toast_key = f"{name}_toast_shown"
    if new_value and not st.session_state[toast_key]:
        st.toast(f"🏆 Achievement unlocked: {name}")
        st.session_state[toast_key] = True

# --- Сетка 3xN ---
cols_per_row = 3
col_index = 0
cols = st.columns(cols_per_row)

for name in achievements.keys():
    col = cols[col_index]
    with col:
        # --- Base64-картинка ---
        img_path = GOLD_IMG if st.session_state[name] else GRAY_IMG
        img_base64 = img_to_base64(img_path)

        # --- Плашка с картинкой и текстом внутри div ---
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                background-color:#2C2C2C;
                border-radius:10px;
                padding:10px;
                height:80px;
                margin-bottom:5px;
            ">
                <img src="data:image/png;base64,{img_base64}" style="width:60px; height:60px; margin-right:15px;" />
                <span style='color:white; font-size:20px; font-weight:bold;'>{name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Отдельный чекбокс под карточкой ---
        st.checkbox(label="Done", key=name, on_change=on_checkbox_change, args=(name,))

    col_index += 1
    if col_index >= cols_per_row:
        col_index = 0
        cols = st.columns(cols_per_row)

# --- Сохранение прогресса ---
for name in achievements.keys():
    achievements[name] = st.session_state[name]

with open(DATA_FILE, "w") as f:
    json.dump(achievements, f, indent=2)