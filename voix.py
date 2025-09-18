import streamlit as st
import pyttsx3
import threading
import time
from datetime import datetime
import sys

# Configuration de la page
st.set_page_config(
    page_title="Assistant Vocal",
    page_icon="🎤",
    layout="centered"
)

# Initialisation du synthétiseur vocal
def init_tts():
    try:
        engine = pyttsx3.init()
        # Configuration de la voix
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
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

# Simulation de reconnaissance vocale (mode texte uniquement)
def simulate_speech_recognition():
    st.info("🎤 Mode simulation - Utilisez la zone de texte ci-dessous")
    return get_text_input()

# Entrée textuelle
def get_text_input():
    text_input = st.text_input("Tapez votre message:", "", key="text_input")
    if text_input:
        return text_input
    return "Aucune entrée détectée"

# Interface Streamlit
def main():
    st.title("🎤 Assistant Vocal Interactif")
    st.markdown("Utilisez la zone de texte pour communiquer avec l'assistant!")
    
    # Initialisation de l'engine TTS
    if 'tts_engine' not in st.session_state:
        st.session_state.tts_engine = init_tts()
    
    # Section de saisie
    st.subheader("💬 Votre message:")
    user_input = get_text_input()
    
    # Bouton pour envoyer
    if st.button("🚀 Envoyer", use_container_width=True, type="primary"):
        if user_input and user_input != "Aucune entrée détectée":
            # Affichage de l'entrée utilisateur
            st.subheader("🎤 Vous avez dit:")
            st.write(f"**{user_input}**")
            
            # Génération de la réponse
            response = f"J'ai bien reçu votre message: '{user_input}'. Comment puis-je vous aider aujourd'hui?"
            
            st.subheader("🤖 Réponse:")
            st.write(f"**{response}**")
            
            # Réponse vocale
            if st.session_state.tts_engine:
                threading.Thread(
                    target=speak, 
                    args=(response, st.session_state.tts_engine),
                    daemon=True
                ).start()
            else:
                st.info("La synthèse vocale n'est pas disponible sur cette plateforme")
        else:
            st.warning("Veuillez taper un message d'abord!")
    
    # Section d'information
    st.markdown("---")
    st.info("""
    **Instructions:**
    - Tapez votre message dans la zone de texte
    - Cliquez sur le bouton **Envoyer**
    - L'assistant répondra vocalement (si supporté)
    - Fonctionne sur toutes les plateformes
    """)
    
    # Debug info
    with st.expander("Informations techniques"):
        st.write(f"Python version: {sys.version}")
        st.write(f"Platform: {sys.platform}")

if __name__ == "__main__":
    main()
