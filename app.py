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
                data = json.load(f)
                # Миграция данных: добавляем поле category для достижений, у которых его нет
                for name, achievement in data.items():
                    if "category" not in achievement:
                        achievement["category"] = "General"  # Категория по умолчанию для старых достижений
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка чтения JSON файла: {e}")
            st.error("Файл данных поврежден. Используем стандартные достижения.")
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
            st.error("Не удалось загрузить данные. Проверьте права доступа к файлу.")
    
    # Возвращаем стандартные достижения при ошибках
    return {
        "Run 10 km": {"done": False, "description": "Пробежал 10 километров за один раз.", "img_gray": None, "img_gold": None, "category": "Fitness"},
        "Read 5 books": {"done": False, "description": "Прочитал 5 книг.", "img_gray": None, "img_gold": None, "category": "Learning"},
        "Meditate 7 days": {"done": False, "description": "Медитировал 7 дней подряд.", "img_gray": None, "img_gold": None, "category": "Health"}
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
        if f"{name}_show_edit" not in st.session_state:
            st.session_state[f"{name}_show_edit"] = False
        if f"{name}_show_delete" not in st.session_state:
            st.session_state[f"{name}_show_delete"] = False

init_session_state()

# --- Колбэки для редактирования ---
def show_edit_popup(name):
    st.session_state[f"{name}_show_edit"] = True

def close_edit_popup(name):
    st.session_state[f"{name}_show_edit"] = False

# --- Колбэки для удаления ---
def show_delete_popup(name):
    st.session_state[f"{name}_show_delete"] = True

def close_delete_popup(name):
    st.session_state[f"{name}_show_delete"] = False

# --- Функция для редактирования достижения ---
def edit_achievement(name, new_name, new_desc, new_category, new_gray_file, new_gold_file):
    """Редактирует достижение с валидацией"""
    # Проверка на пустое имя
    if not new_name.strip():
        st.error("Название достижения не может быть пустым.")
        return False
    
    # Проверка на пустую категорию
    if not new_category.strip():
        new_category = "General"  # Категория по умолчанию если пользователь не ввел категорию
    
    # Проверка на изменение имени и существование нового имени
    if new_name != name and new_name in achievements:
        st.error("Достижение с таким названием уже существует.")
        return False
    
    # Обработка изображений
    img_gray_b64 = process_image_file(new_gray_file, "серого изображения")
    img_gold_b64 = process_image_file(new_gold_file, "золотого изображения")
    
    # Сохраняем старое имя для очистки session_state
    old_name = name
    
    # Обновляем достижение
    achievements[new_name] = {
        "done": achievements[old_name]["done"],
        "description": new_desc,
        "category": new_category,
        "img_gray": img_gray_b64 if img_gray_b64 else achievements[old_name]["img_gray"],
        "img_gold": img_gold_b64 if img_gold_b64 else achievements[old_name]["img_gold"]
    }
    
    # Удаляем старое достижение если имя изменилось
    if new_name != old_name:
        del achievements[old_name]
        # Обновляем session_state
        st.session_state[new_name] = st.session_state[old_name]
        st.session_state[f"{new_name}_toast_shown"] = st.session_state[f"{old_name}_toast_shown"]
        st.session_state[f"{new_name}_show_popup"] = st.session_state[f"{old_name}_show_popup"]
        # Удаляем старые session_state переменные
        del st.session_state[old_name]
        del st.session_state[f"{old_name}_toast_shown"]
        del st.session_state[f"{old_name}_show_popup"]
        del st.session_state[f"{old_name}_show_edit"]
        del st.session_state[f"{old_name}_show_delete"]
    
    # Сохраняем данные
    if save_data():
        st.success(f"Achievement '{new_name}' updated successfully!")
        return True
    return False

# --- Функция для удаления достижения ---
def delete_achievement(name):
    """Удаляет достижение с очисткой session_state"""
    if name in achievements:
        # Удаляем из данных
        del achievements[name]
        # Очищаем session_state
        if name in st.session_state:
            del st.session_state[name]
        if f"{name}_toast_shown" in st.session_state:
            del st.session_state[f"{name}_toast_shown"]
        if f"{name}_show_popup" in st.session_state:
            del st.session_state[f"{name}_show_popup"]
        if f"{name}_show_edit" in st.session_state:
            del st.session_state[f"{name}_show_edit"]
        if f"{name}_show_delete" in st.session_state:
            del st.session_state[f"{name}_show_delete"]
        
        # Сохраняем данные
        if save_data():
            st.success(f"Achievement '{name}' deleted successfully!")
            return True
    return False

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
    new_category = st.text_input("Category", value="General")
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
                "category": new_category if new_category.strip() else "General",
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

for i, name in enumerate(list(achievements.keys())):
    col = cols[col_index]
    with col:
        try:
            # Выбираем картинку: Base64 из JSON или дефолтные
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
                    <div style='flex:1; display:flex; flex-direction:column; justify-content:center;'>
                        <span style='color:white; font-size:22px; font-weight:bold;'>{name}</span>
                        <span style='color:#cccccc; font-size:14px;'>Category: {achievements[name]['category']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Чекбокс + Details + Edit + Delete
            cols_inner = st.columns([1,1,1,1])
            with cols_inner[0]:
                st.checkbox(label="Done", key=name, on_change=on_checkbox_change, args=(name,))
            with cols_inner[1]:
                st.button("Details", key=f"details_{name}", on_click=show_popup, args=(name,))
            with cols_inner[2]:
                st.button("✏️ Edit", key=f"edit_{name}", on_click=show_edit_popup, args=(name,))
            with cols_inner[3]:
                st.button("🗑️ Delete", key=f"delete_{name}", on_click=show_delete_popup, args=(name,))

            # Pop-up
            if st.session_state.get(f"{name}_show_popup", False):
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

            # Edit Modal
            if st.session_state.get(f"{name}_show_edit", False):
                with st.expander(f"✏️ Edit Achievement: {name}", expanded=True):
                    # Форма редактирования
                    edit_name = st.text_input("Title", value=name, key=f"edit_name_{name}")
                    edit_desc = st.text_area("Description", value=achievements[name]["description"], key=f"edit_desc_{name}")
                    edit_category = st.text_input("Category", value=achievements[name]["category"], key=f"edit_category_{name}")
                    edit_gray_file = st.file_uploader("Upload new gray (not done) image", type=["png","jpg","jpeg"], key=f"edit_gray_{name}")
                    edit_gold_file = st.file_uploader("Upload new gold (done) image", type=["png","jpg","jpeg"], key=f"edit_gold_{name}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save Changes", key=f"save_edit_{name}"):
                            if edit_achievement(name, edit_name, edit_desc, edit_category, edit_gray_file, edit_gold_file):
                                close_edit_popup(name)
                    with col2:
                        st.button("Cancel", key=f"cancel_edit_{name}", on_click=close_edit_popup, args=(name,))

            # Delete Modal
            if st.session_state.get(f"{name}_show_delete", False):
                with st.expander(f"🗑️ Delete Achievement: {name}", expanded=True):
                    st.warning(f"Are you sure you want to delete '{name}'?")
                    st.error("This action cannot be undone.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, Delete", key=f"confirm_delete_{name}"):
                            if delete_achievement(name):
                                close_delete_popup(name)
                    with col2:
                        st.button("Cancel", key=f"cancel_delete_{name}", on_click=close_delete_popup, args=(name,))

        except Exception as e:
            logger.error(f"Ошибка при отображении достижения {name}: {e}")
            # Скрываем ошибку от пользователя, но логируем ее
            pass

    col_index += 1
    if col_index >= cols_per_row:
        col_index = 0
        cols = st.columns(cols_per_row)
        st.markdown(f"<div style='margin-bottom:{row_margin}px;'></div>", unsafe_allow_html=True)

# --- Сохраняем прогресс при завершении ---
def save_all_progress():
    """Сохраняет прогресс всех достижений"""
    # Создаем копию ключей, чтобы избежать изменения словаря во время итерации
    achievement_names = list(achievements.keys())
    for name in achievement_names:
        if name in achievements:  # Проверяем, что достижение еще существует
            achievements[name]["done"] = st.session_state[name]
    save_data()

# Автоматическое сохранение при завершении работы
save_all_progress()