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

# Fonction pour générer de l'audio avec gTTS
def text_to_speech(text, language='fr'):
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        st.error(f"Erreur de synthèse vocale: {e}")
        return None

# Fonction pour afficher l'audio
def display_audio(audio_file):
    if audio_file and os.path.exists(audio_file):
        try:
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            
            # Afficher le lecteur audio avec des instructions claires
            st.markdown("### 🔊 Écoutez la réponse:")
            st.markdown("**Cliquez sur le bouton play ▶️ pour entendre la réponse**")
            st.audio(audio_bytes, format="audio/mp3")
            
            # Option pour télécharger l'audio
            st.download_button(
                label="📥 Télécharger l'audio",
                data=audio_bytes,
                file_name="reponse_assistant.mp3",
                mime="audio/mp3"
            )
            
        except Exception as e:
            st.error(f"Erreur: {e}")

# Interface Streamlit
def main():
    st.title("🎤 Assistant Vocal PARLANT")
    st.markdown("**Tapez votre message et l'assistant vous répondra vocalement!**")
    
    # Initialisation
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None
    if 'last_response' not in st.session_state:
        st.session_state.last_response = ""
    
    # Section de saisie
    st.subheader("💬 Votre message:")
    user_input = st.text_input("Tapez votre message ici:", "", key="text_input")
    
    # Bouton principal
    if st.button("🚀 Parler à l'assistant", use_container_width=True, type="primary"):
        if user_input and user_input.strip() != "":
            # Affichage de l'entrée utilisateur
            st.subheader("🎤 Vous avez dit:")
            st.success(f"**{user_input}**")
            
            # Génération de la réponse
            response = f"Bonjour ! J'ai bien reçu votre message : {user_input}. Comment puis-je vous aider aujourd'hui ?"
            
            st.subheader("🤖 Réponse:")
            st.info(f"**{response}**")
            
            # Génération de l'audio
            with st.spinner("🔄 Génération de la réponse audio..."):
                audio_file = text_to_speech(response)
                
                if audio_file:
                    st.session_state.audio_file = audio_file
                    st.session_state.last_response = response
                    st.success("✅ Audio généré avec succès!")
                    
                    # Afficher le lecteur audio
                    display_audio(audio_file)
                else:
                    st.error("❌ Erreur lors de la génération audio")
            
        else:
            st.warning("⚠️ Veuillez taper un message d'abord!")
    
    # Afficher le dernier audio généré si disponible
    if st.session_state.audio_file and os.path.exists(st.session_state.audio_file):
        st.markdown("---")
        st.subheader("🎵 Dernière réponse audio")
        display_audio(st.session_state.audio_file)
    
    # Section d'information améliorée
    st.markdown("---")
    st.info("""
    **🎯 Instructions:**
    1. **Tapez** votre message dans la zone de texte
    2. **Cliquez** sur le bouton *Parler à l'assistant*
    3. **Attendez** que l'audio soit généré (message de succès ✅)
    4. **Cliquez sur le bouton play ▶️** dans le lecteur audio pour écouter
    5. **Téléchargez** l'audio si vous le souhaitez
    
    **ℹ️ Note:** La lecture audio nécessite une action manuelle (cliquez sur play)
    pour des raisons de sécurité des navigateurs.
    """)
    
    # Debug info
    with st.expander("📊 Statut technique"):
        st.write(f"🔧 Audio généré: {'OUI' if st.session_state.audio_file else 'NON'}")
        st.write(f"🗣️ Dernière réponse: {st.session_state.last_response[:50]}...")

if __name__ == "__main__":
    main()
