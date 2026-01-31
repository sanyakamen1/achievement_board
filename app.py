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

# --- Описания достижений ---
descriptions = {
    "Run 10 km": "Пробежал 10 километров за один раз.",
    "Read 5 books": "Прочитал 5 книг.",
    "Meditate 7 days": "Медитировал 7 дней подряд.",
    "Write 1000 words": "Написал 1000 слов.",
    "Learn Python basics": "Выучил основы Python.",
    "Cook a new recipe": "Приготовил новое блюдо.",
    "Draw a sketch": "Нарисовал набросок.",
}

# --- Загрузка прогресса ---
if DATA_FILE.exists():
    with open(DATA_FILE, "r") as f:
        achievements = json.load(f)
else:
    achievements = {k: False for k in descriptions.keys()}

# --- Инициализация session_state ---
for name in achievements.keys():
    if name not in st.session_state:
        st.session_state[name] = achievements[name]
    if f"{name}_toast_shown" not in st.session_state:
        st.session_state[f"{name}_toast_shown"] = achievements[name]
    if f"{name}_show_popup" not in st.session_state:
        st.session_state[f"{name}_show_popup"] = False

# --- Base64 картинка ---
def img_to_base64(path: Path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Чекбокс + toast ---
def on_checkbox_change(name):
    if st.session_state[name] and not st.session_state[f"{name}_toast_shown"]:
        st.toast(f"🏆 Achievement unlocked: {name}")
        st.session_state[f"{name}_toast_shown"] = True

# --- Сетка 3xN ---
cols_per_row = 3
col_index = 0
cols = st.columns(cols_per_row)

for i, name in enumerate(achievements.keys()):
    col = cols[col_index]
    with col:
        img_path = GOLD_IMG if st.session_state[name] else GRAY_IMG
        img_base64 = img_to_base64(img_path)

        # --- Плашка с картинкой и текстом ---
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

        # --- Горизонтальный контейнер для чекбокса и кнопки Details ---
        container = st.container()
        cols_inner = container.columns([1, 1])  # 2 колонки одинаковой ширины
        with cols_inner[0]:
            st.checkbox(label="Done", key=name, on_change=on_checkbox_change, args=(name,))
        with cols_inner[1]:
            if st.button("Details", key=f"details_{name}"):
                st.session_state[f"{name}_show_popup"] = True

        # --- Псевдо-попап под карточкой ---
        if st.session_state[f"{name}_show_popup"]:
            st.markdown(
                f"""
                <div style="
                    background-color:#3C3C3C;
                    padding:20px;
                    border-radius:15px;
                    margin-top:10px;
                    text-align:center;
                ">
                    <img src="data:image/png;base64,{img_base64}" style="width:200px; height:200px; margin-bottom:15px;" />
                    <h2 style="color:white;">{name}</h2>
                    <p style="color:white;">{descriptions[name]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Close", key=f"close_{name}"):
                st.session_state[f"{name}_show_popup"] = False

    col_index += 1
    if col_index >= cols_per_row:
        col_index = 0
        cols = st.columns(cols_per_row)

# --- Сохранение прогресса ---
for name in achievements.keys():
    achievements[name] = st.session_state[name]

with open(DATA_FILE, "w") as f:
    json.dump(achievements, f, indent=2)