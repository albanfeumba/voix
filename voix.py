import streamlit as st
import pyttsx3
import threading
import tempfile
import os
from audio_recorder_streamlit import audio_recorder
import sys

# Configuration de la page
st.set_page_config(
    page_title="Assistant Vocal avec Enregistrement",
    page_icon="🎤",
    layout="centered"
)

# Initialisation du synthétiseur vocal
def init_tts():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        return engine
    except Exception as e:
        st.warning(f"Synthèse vocale limitée: {e}")
        return None

# Fonction pour parler
def speak(text, engine):
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            st.error(f"Erreur de synthèse: {e}")
    else:
        st.info(f"Réponse textuelle: {text}")

def main():
    st.title("🎤 Assistant Vocal avec Enregistrement")
    
    # Initialisation
    if 'tts_engine' not in st.session_state:
        st.session_state.tts_engine = init_tts()
    
    # Mode choix
    mode = st.radio("Choisissez le mode:", ["Texte", "Enregistrement Audio"])
    
    if mode == "Texte":
        user_input = st.text_input("Tapez votre message:", "")
        
        if st.button("🚀 Envoyer") and user_input:
            response = f"Message reçu: {user_input}. Comment vous aider?"
            st.write(f"**Réponse:** {response}")
            
            if st.session_state.tts_engine:
                threading.Thread(
                    target=speak, 
                    args=(response, st.session_state.tts_engine)
                ).start()
    
    else:
        st.info("Enregistrez votre message audio (fonctionnalité avancée)")
        user_input = st.text_input("Ou tapez votre message:", "")
        
        if user_input:
            response = f"Message audio simulé: {user_input}"
            st.write(f"**Réponse:** {response}")
            
            if st.session_state.tts_engine:
                threading.Thread(
                    target=speak, 
                    args=(response, st.session_state.tts_engine)
                ).start()

if __name__ == "__main__":
    main()
