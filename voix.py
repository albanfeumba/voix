import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import time
from datetime import datetime
import os
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

# Fonction de reconnaissance vocale avec fallback
def recognize_speech():
    recognizer = sr.Recognizer()
    
    try:
        # Essayer d'abord sans microphone (pour tests)
        with sr.Microphone() as source:
            st.info("🎤 Écoute en cours... Parlez maintenant!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                return "Délai d'attente dépassé. Veuillez réessayer."
    except (OSError, AttributeError):
        # Fallback: entrée textuelle si microphone indisponible
        st.warning("Microphone non disponible. Utilisation du mode texte.")
        return get_text_input()
    
    try:
        text = recognizer.recognize_google(audio, language='fr-FR')
        return text
    except sr.UnknownValueError:
        return "Je n'ai pas compris ce que vous avez dit."
    except sr.RequestError:
        return "Erreur de service de reconnaissance vocale."

# Fallback pour entrée textuelle
def get_text_input():
    text_input = st.text_input("Parlez-moi (tapez votre message):", "")
    if text_input:
        return text_input
    return "Aucune entrée détectée"

# Interface Streamlit
def main():
    st.title("🎤 Assistant Vocal Interactif")
    st.markdown("Cliquez sur le bouton **Run** pour parler et obtenir une réponse!")
    
    # Initialisation de l'engine TTS
    if 'tts_engine' not in st.session_state:
        st.session_state.tts_engine = init_tts()
    
    # Vérification des dépendances
    try:
        sr.Microphone()
        st.success("✅ Microphone détecté")
    except:
        st.warning("⚠️ Microphone non disponible - Mode texte activé")
    
    # Bouton principal
    if st.button("🎤 Run", use_container_width=True, type="primary"):
        with st.spinner("Écoute en cours..."):
            user_input = recognize_speech()
        
        # Affichage de l'entrée utilisateur
        st.subheader("🎤 Vous avez dit:")
        st.write(f"**{user_input}**")
        
        # Génération de la réponse
        if any(phrase in user_input.lower() for phrase in ["je n'ai pas compris", "délai d'attente", "aucune entrée"]):
            response = "Je n'ai pas bien compris votre message. Pouvez-vous répéter?"
        else:
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
    
    # Section d'information
    st.markdown("---")
    st.info("""
    **Instructions:**
    - Cliquez sur le bouton **Run**
    - Parlez clairement dans votre microphone
    - L'assistant répondra vocalement
    - Mode texte disponible si microphone indisponible
    """)
    
    # Debug info
    with st.expander("Informations techniques"):
        st.write(f"Python version: {sys.version}")
        st.write(f"Platform: {sys.platform}")

if __name__ == "__main__":
    main()
