import streamlit as st
from pathlib import Path
import json
import base64
import os
import logging

# --- Настройка страницы ---
st.set_page_config(page_title="Achievements", layout="wide")
st.title("🏆 Achievement Board")

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
GRAY_IMG = BASE_DIR / "images/gray.png"
GOLD_IMG = BASE_DIR / "images/gold.png"
DATA_FILE = BASE_DIR / "data.json"

# --- Централизованная функция для сохранения данных ---
def save_data():
    """Сохраняет данные в JSON файл с обработкой ошибок"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(achievements, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}")
        st.error("Не удалось сохранить данные. Проверьте права доступа к файлу.")
        return False

# --- Загрузка данных из JSON ---
def load_data():
    """Загружает данные из JSON файла с обработкой ошибок"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка чтения JSON файла: {e}")
            st.error("Файл данных поврежден. Используем стандартные достижения.")
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
            st.error("Не удалось загрузить данные. Проверьте права доступа к файлу.")
    
    # Возвращаем стандартные достижения при ошибках
    return {
        "Run 10 km": {"done": False, "description": "Пробежал 10 километров за один раз.", "img_gray": None, "img_gold": None},
        "Read 5 books": {"done": False, "description": "Прочитал 5 книг.", "img_gray": None, "img_gold": None},
        "Meditate 7 days": {"done": False, "description": "Медитировал 7 дней подряд.", "img_gray": None, "img_gold": None}
    }

achievements = load_data()

# --- Base64 картинка с обработкой ошибок ---
def img_to_base64(path: Path):
    """Конвертирует изображение в Base64 с обработкой ошибок"""
    try:
        if not path.exists():
            logger.warning(f"Изображение не найдено: {path}")
            return None
        
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        logger.error(f"Ошибка при чтении изображения {path}: {e}")
        return None

# --- Инициализация session_state ---
def init_session_state():
    """Инициализирует session_state для всех достижений"""
    for name in achievements.keys():
        if name not in st.session_state:
            st.session_state[name] = achievements[name]["done"]
        if f"{name}_toast_shown" not in st.session_state:
            st.session_state[f"{name}_toast_shown"] = achievements[name]["done"]
        if f"{name}_show_popup" not in st.session_state:
            st.session_state[f"{name}_show_popup"] = False

init_session_state()

# --- Чекбокс + toast ---
def on_checkbox_change(name):
    """Обработчик изменения состояния чекбокса"""
    if st.session_state[name] and not st.session_state[f"{name}_toast_shown"]:
        st.toast(f"🏆 Achievement unlocked: {name}")
        st.session_state[f"{name}_toast_shown"] = True
        # Сохраняем прогресс
        achievements[name]["done"] = True
        save_data()

# --- Колбэки для pop-up ---
def show_popup(name):
    st.session_state[f"{name}_show_popup"] = True

def close_popup(name):
    st.session_state[f"{name}_show_popup"] = False

# --- Функция для валидации и конвертации изображений ---
def process_image_file(uploaded_file, image_type):
    """Обрабатывает загруженный файл изображения"""
    if not uploaded_file:
        return None
    
    try:
        # Проверяем размер файла (не более 5MB)
        if uploaded_file.size > 5 * 1024 * 1024:
            st.warning(f"Файл {image_type} слишком большой. Максимальный размер: 5MB")
            return None
        
        # Читаем и конвертируем в Base64
        image_data = uploaded_file.read()
        if not image_data:
            st.warning(f"Файл {image_type} пустой или поврежден.")
            return None
        
        return base64.b64encode(image_data).decode()
    
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения {image_type}: {e}")
        st.error(f"Ошибка при обработке изображения {image_type}. Пожалуйста, загрузите файл заново.")
        return None

# --- Создание новой ачивки в боковой панели ---
with st.sidebar:
    st.header("➕ Add New Achievement")
    new_name = st.text_input("Title")
    new_desc = st.text_area("Description")
    gray_file = st.file_uploader("Upload gray (not done) image", type=["png","jpg","jpeg"])
    gold_file = st.file_uploader("Upload gold (done) image", type=["png","jpg","jpeg"])
    
    if st.button("Create Achievement"):
        # Валидация ввода
        if not new_name.strip():
            st.error("Название достижения не может быть пустым.")
        elif new_name in achievements:
            st.error("Достижение с таким названием уже существует.")
        else:
            # Обработка изображений
            img_gray_b64 = process_image_file(gray_file, "серого изображения")
            img_gold_b64 = process_image_file(gold_file, "золотого изображения")
            
            # Создаем новое достижение
            achievements[new_name] = {
                "done": False,
                "description": new_desc,
                "img_gray": img_gray_b64,
                "img_gold": img_gold_b64
            }
            
            # Инициализация session_state для нового достижения
            st.session_state[new_name] = False
            st.session_state[f"{new_name}_toast_shown"] = False
            st.session_state[f"{new_name}_show_popup"] = False
            
            # Сохраняем данные
            if save_data():
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
        try:
            if achievements[name]["img_gray"] and achievements[name]["img_gold"]:
                img_base64 = achievements[name]["img_gold"] if st.session_state[name] else achievements[name]["img_gray"]
            else:
                # Используем дефолтные изображения
                default_img_path = GOLD_IMG if st.session_state[name] else GRAY_IMG
                img_base64 = img_to_base64(default_img_path)
                
                # Если дефолтное изображение недоступно, используем заглушку
                if not img_base64:
                    img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # Пустое изображение
            
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

        except Exception as e:
            logger.error(f"Ошибка при отображении достижения {name}: {e}")
            st.error(f"Ошибка при отображении достижения: {name}")

    col_index += 1
    if col_index >= cols_per_row:
        col_index = 0
        cols = st.columns(cols_per_row)
        st.markdown(f"<div style='margin-bottom:{row_margin}px;'></div>", unsafe_allow_html=True)

# --- Сохраняем прогресс при завершении ---
def save_all_progress():
    """Сохраняет прогресс всех достижений"""
    for name in achievements.keys():
        achievements[name]["done"] = st.session_state[name]
    save_data()

# Автоматическое сохранение при завершении работы
save_all_progress()
