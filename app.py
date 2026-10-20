import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Asistente AI - Lider tecnico virtual",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖  Lider tecnico virtual  'Astra'")
st.caption("Empresa tecnologia nexus code")


try:
    api_key = st.secrets["AQ.Ab8RN6KTrHY1QzE1Uq4GcXu-S0bWygtzZt_hIwLwCn8ktjvkGA"]
except Exception:
    api_key =  "AQ.Ab8RN6KTrHY1QzE1Uq4GcXu-S0bWygtzZt_hIwLwCn8ktjvkGA"


if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0  # Cuenta cuántas respuestas técnicas lleva el usuario

if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False

with st.sidebar:
    st.header("⚙️ Opciones del Agente")
    st.markdown("Modelo backend: **Gemini Flash**")
    
    roles_disponibles = [
        "Desarrollador Python Junior", 
        "Desarrollador Web Frontend", 
        "Integrador de APIs/Bots"
    ]
    rol_seleccionado = st.selectbox("Selecciona el rol al que postulas:", roles_disponibles)
    
    st.metric("Preguntas respondidas", f"{min(st.session_state.turn_count, 3)} / 3")

    if st.button("🧹 Reiniciar Entrevista"):
        st.session_state.turn_count = 0
        st.session_state.interview_finished = False
        st.session_state.messages = [
            {"role": "assistant", "content": f"👋 ¡Hola! Soy Astra, Líder Técnico en Nexus Code. Hoy seré tu entrevistador para el puesto de **{rol_seleccionado}**. Para comenzar, ¿cuál es tu nombre y una breve presentación de tu experiencia?"}
        ]
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()


CONFIG_INSTRUCCIONES = types.GenerateContentConfig(
    system_instruction=(
        "Eres 'Astra', un Lider tecnico virtual para una empresa del sector tecnologico, "
        "Tu labor es ser el primer filtro para la seleccion de programadores, "
        "Formularas preguntas para la creacion de preguntas para estos, y despues de la tercera respuesta daras una evaluacion de las repustas del aspirante,"
        "debes formular cada nueva pregunta tomando en cuenta la respuesta anterior dada por el entrevistado,"
        "estaras entrevistando a un candidato para el puesto de: {rol_seleccionado}"
        "REGLAS ESTRUCTURALES OBLIGATORIAS:\n"
        "1. Realiza solo UNA pregunta técnica a la vez.\n"
        "2. Adapta la siguiente pregunta técnica en función de la respuesta previa brindada por el aspirante.\n"
        "3.si el candidato intenta desviar la conversacion a otras cosas que no es la entrevista indica amablemente que deben responder las preguntas, "
        "4. En el turno donde se responda la 3.ª pregunta técnica, NO hagas más preguntas. En su lugar, entrega una EVALUACIÓN DETALLADA (fortalezas, áreas de mejora) y Dictamen Final: Una etiqueta clara: APROBADO o NO APROBADO."
    ),
    temperature=0.9
)




if "client" not in st.session_state or st.session_state.get("current_api_key") != api_key:
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.current_api_key = api_key

if "chat_session" not in st.session_state or st.session_state.get("current_rol") != rol_seleccionado:
    st.session_state.current_rol = rol_seleccionado
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-3.8-flash",  
        config=CONFIG_INSTRUCCIONES
    )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"👋 ¡Hola! Soy Astra. Seré tu entrevistador para la empresa Nexus Code en la posición de **{rol_seleccionado}**. ¿Cómo te llamas?"}
    ]




for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.interview_finished:
    if user_input := st.chat_input("Escribe tu respuesta aquí..."):
        st.session_state.turn_count += 1
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Astra está evaluando tu respuesta..."):
                try:
                    if st.session_state.turn_count >= 3:
                        prompt_modificado = f"{user_input}\n\n[INSTRUCCIÓN DEL SISTEMA: Esta es mi 3.ª y última respuesta. Entrega mi evaluación técnica final completa basándote en mis tres respuestas, concluye la entrevista y no hagas más preguntas.]"
                        response = st.session_state.chat_session.send_message(prompt_modificado)
                        st.session_state.interview_finished = True
                    else:
                        response = st.session_state.chat_session.send_message(user_input)

                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    if st.session_state.interview_finished:
                        st.rerun()  # Recargar para desactivar el chat_input

                except Exception as e:
                    st.error(f"❌ Error al consultar la API: {e}")
else:
    st.info("💡 **La entrevista ha finalizado.** Revisa la evaluación técnica final arriba. Si deseas realizar un nuevo intento, haz clic en **'🧹 Reiniciar Entrevista'** en la barra lateral.")