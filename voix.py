import streamlit as st
import base64
import io
from gtts import gTTS
import tempfile
import os

# Configuration de la page
st.set_page_config(
    page_title="Assistant Vocal Parlant",
    page_icon="🎤",
    layout="centered"
)

# Fonction pour générer de l'audio avec gTTS (Google Text-to-Speech)
def text_to_speech(text, language='fr'):
    try:
        # Créer l'audio avec gTTS
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Sauvegarder dans un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        st.error(f"Erreur de synthèse vocale: {e}")
        return None

# Fonction pour lire l'audio
def play_audio(audio_file):
    if audio_file and os.path.exists(audio_file):
        try:
            # Lire le fichier audio
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            
            # Afficher le lecteur audio
            st.audio(audio_bytes, format="audio/mp3")
            
            # Nettoyer le fichier temporaire
            os.unlink(audio_file)
            
        except Exception as e:
            st.error(f"Erreur de lecture audio: {e}")

# Interface Streamlit
def main():
    st.title("🎤 Assistant Vocal PARLANT")
    st.markdown("Tapez votre message et l'assistant vous répondra vocalement!")
    
    # Initialisation de la session
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None
    
    # Section de saisie
    st.subheader("💬 Votre message:")
    user_input = st.text_input("Tapez votre message ici:", "", key="text_input")
    
    # Bouton pour envoyer
    if st.button("🚀 Parler à l'assistant", use_container_width=True, type="primary"):
        if user_input and user_input.strip() != "":
            # Affichage de l'entrée utilisateur
            st.subheader("🎤 Vous avez dit:")
            st.write(f"**{user_input}**")
            
            # Génération de la réponse
            response = f"J'ai bien reçu votre message: {user_input}. Comment puis-je vous aider aujourd'hui?"
            
            st.subheader("🤖 Réponse:")
            st.write(f"**{response}**")
            
            # Génération de l'audio
            with st.spinner("🔄 Génération de la réponse audio..."):
                audio_file = text_to_speech(response)
                
                if audio_file:
                    st.session_state.audio_file = audio_file
                    st.success("✅ Audio généré avec succès!")
                    
                    # Jouer l'audio automatiquement
                    st.subheader("🔊 Écoutez la réponse:")
                    play_audio(audio_file)
                else:
                    st.error("❌ Erreur lors de la génération audio")
            
        else:
            st.warning("⚠️ Veuillez taper un message d'abord!")
    
    # Bouton pour rejouer l'audio
    if st.session_state.audio_file and os.path.exists(st.session_state.audio_file):
        if st.button("🔁 Rejouer l'audio"):
            play_audio(st.session_state.audio_file)
    
    # Section d'information
    st.markdown("---")
    st.info("""
    **🎯 Instructions:**
    - Tapez votre message dans la zone de texte
    - Cliquez sur le bouton **Parler à l'assistant**
    - L'assistant répondra vocalement en français
    - Utilisez **🔁 Rejouer l'audio** pour réécouter
    - Fonctionne sur Streamlit Cloud 🚀
    """)

if __name__ == "__main__":
    main()
