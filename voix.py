import streamlit as st
from gtts import gTTS
import base64
import tempfile
import os

# Configuration de la page
st.set_page_config(
    page_title="Assistant Vocal - Écoute Directe",
    page_icon="🎤",
    layout="centered"
)

# Fonction pour générer l'audio et le convertir en base64
def generate_audio_base64(text, language='fr'):
    try:
        # Créer l'audio avec gTTS
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Sauvegarder dans un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            
            # Lire le fichier et convertir en base64
            with open(tmp_file.name, "rb") as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()
            
            # Nettoyer le fichier temporaire
            os.unlink(tmp_file.name)
            
            return audio_base64, audio_bytes
            
    except Exception as e:
        st.error(f"Erreur de synthèse vocale: {e}")
        return None, None

# Fonction pour créer le lecteur audio HTML avec autoplay
def audio_player_with_autoplay(audio_base64):
    html_code = f"""
    <audio id="myAudio" controls autoplay style="width: 100%;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Votre navigateur ne supporte pas l'élément audio.
    </audio>
    <script>
        // Forcer la lecture sur certains navigateurs
        document.addEventListener('DOMContentLoaded', function() {{
            var audio = document.getElementById('myAudio');
            audio.play().catch(function(error) {{
                console.log('Lecture automatique bloquée: ', error);
            }});
        }});
    </script>
    """
    return html_code

# Interface Streamlit
def main():
    st.title("🎤 Assistant Vocal - ÉCOUTE DIRECTE")
    st.markdown("**Parlez et écoutez la réponse immédiatement!**")
    
    # Initialisation
    if 'audio_base64' not in st.session_state:
        st.session_state.audio_base64 = None
    if 'audio_bytes' not in st.session_state:
        st.session_state.audio_bytes = None
    
    # Section de saisie
    st.subheader("💬 Votre message:")
    user_input = st.text_input("Tapez votre message ici:", "", key="text_input")
    
    # Bouton principal
    if st.button("🎤 Parler et Écouter", use_container_width=True, type="primary"):
        if user_input and user_input.strip() != "":
            # Affichage de l'entrée utilisateur
            st.subheader("🎤 Vous avez dit:")
            st.success(f"**{user_input}**")
            
            # Génération de la réponse
            response = f"Bonjour ! J'ai bien compris votre message : {user_input}. Comment puis-je vous aider aujourd'hui ?"
            
            st.subheader("🤖 Réponse:")
            st.info(f"**{response}**")
            
            # Génération de l'audio
            with st.spinner("🔄 Génération de la réponse audio..."):
                audio_base64, audio_bytes = generate_audio_base64(response)
                
                if audio_base64:
                    st.session_state.audio_base64 = audio_base64
                    st.session_state.audio_bytes = audio_bytes
                    st.success("✅ Audio généré ! Écoutez ci-dessous ↓")
                    
                    # Afficher le lecteur audio avec autoplay
                    st.markdown("### 🔊 Écoutez la réponse:")
                    st.components.v1.html(audio_player_with_autoplay(audio_base64), height=80)
                    
                    # Alternative avec le lecteur Streamlit standard
                    st.markdown("**Ou utilisez ce lecteur:**")
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    
                else:
                    st.error("❌ Erreur lors de la génération audio")
            
        else:
            st.warning("⚠️ Veuillez taper un message d'abord!")
    
    # Afficher le dernier audio généré
    if st.session_state.audio_base64:
        st.markdown("---")
        st.subheader("🎵 Réécouter la réponse")
        
        # Lecteur HTML avec autoplay
        st.components.v1.html(audio_player_with_autoplay(st.session_state.audio_base64), height=80)
        
        # Option de téléchargement
        st.download_button(
            label="📥 Télécharger l'audio",
            data=st.session_state.audio_bytes,
            file_name="reponse_assistant.mp3",
            mime="audio/mp3",
            use_container_width=True
        )
    
    # Section d'information
    st.markdown("---")
    st.info("""
    **🎯 Instructions:**
    1. **Tapez** votre message
    2. **Cliquez** sur *Parler et Écouter*
    3. **L'audio démarre automatiquement** (si autorisé par le navigateur)
    4. **Sinon**, cliquez sur le bouton play ▶️
    5. **Réécoutez** ou **téléchargez** si besoin
    
    **ℹ️ Note:** Certains navigateurs peuvent bloquer la lecture automatique.
    Dans ce cas, cliquez manuellement sur le bouton play.
    """)

if __name__ == "__main__":
    main()
