import streamlit as st
from google import genai
from google.genai import types

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==============================================================================
st.set_page_config(
    page_title="Asistente AI - Lider tecnico virtual",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖  Lider tecnico virtual  'Astra'")
st.caption("Empresa tecnologia nexus code")

# ==============================================================================
# 2. GESTIÓN SEGURA DE LA API KEY (LOCAL Y STREAMLIT CLOUD)
# ==============================================================================
try:
    # Intenta leer la clave desde los secretos de Streamlit Cloud
    api_key = st.secrets["AQ.Ab8RN6KTrHY1QzE1Uq4GcXu-S0bWygtzZt_hIwLwCn8ktjvkGA"]
except Exception:
    # ⚠️ REEMPLAZA ESTA CADENA POR TU CLAVE REAL DE GOOGLE AI STUDIO PARA PRUEBAS LOCALES
    api_key =  "AQ.Ab8RN6KTrHY1QzE1Uq4GcXu-S0bWygtzZt_hIwLwCn8ktjvkGA"

rol = "" 

# ==============================================================================
# 3. CONFIGURACIÓN DE PERSONALIDAD DEL BOT
# ==============================================================================
CONFIG_INSTRUCCIONES = types.GenerateContentConfig(
    system_instruction=(
        "Eres 'Astra', un Lider tecnico virtual para una empresa del sector tecnologico, "
        "Tu labor es ser el primer filtro para la seleccion de programadores, "
        "Formularas preguntas para la creacion de preguntas para estos, y despues de la tercera respuesta daras una evaluacion de las repustas del aspirante,"
        "si el candidato intenta desviar la conversacion a otras cosas que no es la entrevista indica amablemente que deben responder las preguntas, "
        "estaras entrevistando a " + rol
    ),
    temperature=0.9
)

# ==============================================================================
# 4. INICIALIZACIÓN PERSISTENTE EN MEMORIA (PREVIENE ERRORES DE CONEXIÓN)
# ==============================================================================
# Se guarda tanto el cliente como el chat en st.session_state para mantenerlos vivos
if "client" not in st.session_state or st.session_state.get("current_api_key") != api_key:
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.current_api_key = api_key
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-3.8-flash",
        config=CONFIG_INSTRUCCIONES
    )

# Historial gráfico de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 ¡Hola! Soy Astra. Sere tu entrevistador para la empresa nexus code ¿Comó te llamas?"}
    ]

# ==============================================================================
# 5. BARRA LATERAL (OPCIONES DE REINICIO)
# ==============================================================================

combobox = st.selectbox({"Desarrollador python Junio" , "Desarrollador Web frontend","Integrador de APIs/Bots"})
with st.sidebar:
    st.header("⚙️ Opciones del Agente")
    st.markdown("Modelo backend: **Gemini 3.8 Flash**")
    if st.button("🧹 Limpiar Conversación"):
        st.session_state.chat_session = st.session_state.client.chats.create(
            model="gemini-3.8-flash",
            config=CONFIG_INSTRUCCIONES
        )
        st.session_state.messages = [
            {"role": "assistant", "content": "🧹 La sesión ha sido reiniciada. Hay que empezar de nuevo las preguntas"}
        ]
        st.rerun()
        
    combobox = st.selectbox({"Desarrollador python Junio" , "Desarrollador Web frontend","Integrador de APIs/Bots"})
    if st.selectbox("Rol a postular:"):
        rol = "Desarrollador python Junio"
        


# ==============================================================================
# 6. RENDERIZADO DEL HISTORIAL DE MENSAJES
# ==============================================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==============================================================================
# 7. ENTRADA DE TEXTO Y PROCESAMIENTO
# ==============================================================================
if user_input := st.chat_input("Escribe tu pregunta o duda aquí..."):
    # Renderizar el mensaje del usuario de inmediato
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generar la respuesta llamando a la API de Gemini
    with st.chat_message("assistant"):
        with st.spinner("Pensando respuesta..."):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"❌ Error al consultar la API: {e}")