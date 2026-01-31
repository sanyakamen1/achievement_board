import streamlit as st
from pathlib import Path
import json
import base64

# --- Настройка страницы ---
st.set_page_config(page_title="Achievements", layout="wide")
st.title("🏆 Achievement Board")

BASE_DIR = Path(__file__).parent
GRAY_IMG = BASE_DIR / "images/gray.png"
GOLD_IMG = BASE_DIR / "images/gold.png"
DATA_FILE = BASE_DIR / "data.json"

# --- Загрузка данных из JSON ---
if DATA_FILE.exists():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        achievements = json.load(f)
else:
    achievements = {
        "Run 10 km": {"done": False, "description": "Пробежал 10 километров за один раз.", "img_gray": None, "img_gold": None},
        "Read 5 books": {"done": False, "description": "Прочитал 5 книг.", "img_gray": None, "img_gold": None},
        "Meditate 7 days": {"done": False, "description": "Медитировал 7 дней подряд.", "img_gray": None, "img_gold": None}
    }

# --- Инициализация session_state ---
for name, info in achievements.items():
    if name not in st.session_state:
        st.session_state[name] = info["done"]
    if f"{name}_toast_shown" not in st.session_state:
        st.session_state[f"{name}_toast_shown"] = info["done"]
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

# --- Колбэки для pop-up ---
def show_popup(name):
    st.session_state[f"{name}_show_popup"] = True

def close_popup(name):
    st.session_state[f"{name}_show_popup"] = False

# --- Создание новой ачивки в боковой панели ---
with st.sidebar:
    st.header("➕ Add New Achievement")
    new_name = st.text_input("Title")
    new_desc = st.text_area("Description")
    gray_file = st.file_uploader("Upload gray (not done) image", type=["png","jpg","jpeg"])
    gold_file = st.file_uploader("Upload gold (done) image", type=["png","jpg","jpeg"])
    if st.button("Create Achievement"):
        if new_name.strip() != "" and new_name not in achievements:
            # Конвертируем картинки в Base64
            img_gray_b64 = base64.b64encode(gray_file.read()).decode() if gray_file else None
            img_gold_b64 = base64.b64encode(gold_file.read()).decode() if gold_file else None

            achievements[new_name] = {
                "done": False,
                "description": new_desc,
                "img_gray": img_gray_b64,
                "img_gold": img_gold_b64
            }

            # Инициализация session_state
            st.session_state[new_name] = False
            st.session_state[f"{new_name}_toast_shown"] = False
            st.session_state[f"{new_name}_show_popup"] = False

            # Сохраняем JSON
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(achievements, f, ensure_ascii=False, indent=2)
            st.success(f"Achievement '{new_name}' added!")

# --- Сетка 3xN с отступами между рядами ---
cols_per_row = 3
col_index = 0
cols = st.columns(cols_per_row)
row_margin = 40

for i, name in enumerate(achievements.keys()):
    col = cols[col_index]
    with col:
        # Выбираем картинку: Base64 из JSON или дефолтные
        if achievements[name]["img_gray"] and achievements[name]["img_gold"]:
            img_base64 = achievements[name]["img_gold"] if st.session_state[name] else achievements[name]["img_gray"]
        else:
            img_base64 = img_to_base64(GOLD_IMG if st.session_state[name] else GRAY_IMG)

        # Плашка
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                background-color:#2C2C2C;
                border-radius:12px;
                padding:15px 20px;
                width:100%;
                height:120px;
                margin-bottom:5px;
            ">
                <img src="data:image/png;base64,{img_base64}" style="width:90px; height:90px; margin-right:20px;" />
                <div style='flex:1; display:flex; justify-content:center; align-items:center;'>
                    <span style='color:white; font-size:22px; font-weight:bold;'>{name}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Чекбокс + Details
        cols_inner = st.columns([1,1])
        with cols_inner[0]:
            st.checkbox(label="Done", key=name, on_change=on_checkbox_change, args=(name,))
        with cols_inner[1]:
            st.button("Details", key=f"details_{name}", on_click=show_popup, args=(name,))

        # Pop-up
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
                    <p style="color:white;">{achievements[name]["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.button("Close", key=f"close_{name}", on_click=close_popup, args=(name,))

    col_index += 1
    if col_index >= cols_per_row:
        col_index = 0
        cols = st.columns(cols_per_row)
        st.markdown(f"<div style='margin-bottom:{row_margin}px;'></div>", unsafe_allow_html=True)

# --- Сохраняем прогресс ---
for name in achievements.keys():
    achievements[name]["done"] = st.session_state[name]

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(achievements, f, ensure_ascii=False, indent=2)