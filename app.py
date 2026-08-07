import streamlit as st
import json
from openai import OpenAI
import os

st.set_page_config(
    page_title="AVENIR — Opportunity Matcher",
    page_icon="🌍",
    layout="centered"
)

st.title("AVENIR — Opportunity Matcher")
st.markdown("**Персональный подбор международных возможностей для студентов и школьников Казахстана**")
st.markdown("---")

# Загрузка базы возможностей
try:
    with open("opportunities.json", "r", encoding="utf-8") as f:
        opportunities = json.load(f)
except:
    opportunities = []

# Форма профиля
with st.form("profile_form"):
    st.subheader("Ваш профиль")

    col1, col2 = st.columns(2)

    with col1:
        education = st.selectbox(
            "Уровень образования",
            ["9–11 класс", "Студент 1–2 курс", "Студент 3–4 курс", "Магистрант / выпускник"]
        )
        english = st.selectbox(
            "Уровень английского",
            ["A2 и ниже", "B1", "B2", "C1+"]
        )

    with col2:
        goal = st.selectbox(
            "Главная цель сейчас",
            [
                "Стипендия / обучение за границей",
                "Стажировка",
                "Онлайн-курс / сертификат",
                "Олимпиада / конкурс",
                "Волонтёрство",
                "Просто развиваться и копить опыт"
            ]
        )
        region = st.radio(
            "Где вы живёте?",
            ["Крупный город (Алматы, Астана и т.д.)", "Небольшой город / село"],
            horizontal=True
        )

    interests = st.multiselect(
        "Интересы (можно выбрать несколько)",
        ["IT / AI", "Бизнес и экономика", "Медицина", "Дизайн и творчество", 
         "Гуманитарные науки", "Инженерия", "Экология", "Право", "Другое"]
    )

    time_available = st.select_slider(
        "Сколько времени готовы уделять в неделю?",
        options=["1–3 часа", "4–7 часов", "8+ часов"]
    )

    submitted = st.form_submit_button("Найти возможности 🚀", use_container_width=True)

if submitted:
    if not opportunities:
        st.warning("База возможностей пока пустая. Добавьте данные в opportunities.json")
    else:
        with st.spinner("AVENIR подбирает возможности под ваш профиль..."):

            # Формируем текст базы
            opp_text = ""
            for o in opportunities:
                opp_text += f"""
ID: {o.get('id')}
Название: {o.get('title')}
Тип: {o.get('type')}
Дедлайн: {o.get('deadline')}
Уровень: {o.get('level')}
Язык: {o.get('language')}
Теги: {', '.join(o.get('tags', []))}
Описание: {o.get('description')}
Ссылка: {o.get('link')}
Почему полезно: {o.get('why_good')}
---
"""

            system_prompt = """Ты — AVENIR, умный помощник по международным возможностям для студентов и школьников Казахстана.
Отвечай только на русском языке.
Структура ответа строго соблюдай:

1. Краткий анализ профиля (2-3 предложения)
2. Топ-5-7 наиболее подходящих возможностей. Для каждой укажи:
   - Название
   - Почему подходит именно этому человеку
   - Дедлайн
   - Ссылку
3. Конкретный план действий на ближайшие 2-4 недели (что делать шаг за шагом)

Будь честным и полезным. Если подходящих возможностей мало — скажи об этом прямо."""

            user_prompt = f"""
Профиль пользователя:
- Образование: {education}
- Английский: {english}
- Цель: {goal}
- Регион: {region}
- Интересы: {', '.join(interests) if interests else 'не указаны'}
- Доступное время: {time_available}

База возможностей:
{opp_text}
"""

            try:
                client = OpenAI(
                    api_key=st.secrets["GROQ_API_KEY"],
                    base_url="https://api.groq.com/openai/v1"
                )

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.4,
                    max_tokens=1500
                )

                result = response.choices[0].message.content
                st.markdown("---")
                st.markdown(result)

            except Exception as e:
                st.error(f"Ошибка при обращении к AI: {e}")
                st.info("Проверьте, что API-ключ правильно добавлен в Secrets на Streamlit Cloud.")
