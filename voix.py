import streamlit as st
import threading
import time
from datetime import datetime
import os
import sys

# Configuration de la page
st.set_page_config(
    page_title="Assistant Vocal Interactif",
    page_icon="🎤",
    layout="centered"
)

# Interface Streamlit
def main():
    st.title("🎤 Assistant Vocal Interactif")
    st.markdown("Utilisez la zone de texte pour communiquer avec l'assistant!")
    
    # Section de saisie
    st.subheader("💬 Votre message:")
    user_input = st.text_input("Tapez votre message:", "", key="text_input")
    
    # Bouton pour envoyer
    if st.button("🚀 Envoyer", use_container_width=True, type="primary"):
        if user_input and user_input.strip() != "":
            # Affichage de l'entrée utilisateur
            st.subheader("🎤 Vous avez dit:")
            st.write(f"**{user_input}**")
            
            # Génération de la réponse
            response = f"J'ai bien reçu votre message: '{user_input}'. Comment puis-je vous aider aujourd'hui?"
            
            st.subheader("🤖 Réponse:")
            st.write(f"**{response}**")
            
            # Simulation de réponse vocale
            st.success("🗣️ Réponse vocale simulée (l'audio serait joué ici)")
            
        else:
            st.warning("Veuillez taper un message d'abord!")
    
    # Section d'information
    st.markdown("---")
    st.info("""
    **Instructions:**
    - Tapez votre message dans la zone de texte
    - Cliquez sur le bouton **Envoyer**
    - L'assistant affichera une réponse
    - Version simplifiée pour Streamlit Cloud
    """)
    
    # Debug info
    with st.expander("📊 Informations techniques"):
        st.write(f"Python version: {sys.version}")
        st.write(f"Platform: {sys.platform}")
        st.write(f"Streamlit version: {st.__version__}")

if __name__ == "__main__":
    main()
