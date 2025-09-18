import streamlit as st
from gtts import gTTS
import base64
import tempfile
import os
import io
import numpy as np
import soundfile as sf

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
    whisper_model = whisper.load_model("base")
except ImportError:
    WHISPER_AVAILABLE = False

from audiorecorder import audiorecorder  # Composant pour enregistrement navigateur

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Assistant Vocal - Écoute Directe",
    page_icon="🎤",
    layout="centered"
)

# ---------------- UTILS ----------------
def generate_audio_base64(text, language='fr'):
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            with open(tmp_file.name, "rb") as f:
                audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()
        os.unlink(tmp_file.name)
        return audio_base64, audio_bytes
    except Exception as e:
        st.error(f"Erreur synthèse vocale: {e}")
        return None, None

def audio_player_with_autoplay(audio_base64):
    return f"""
    <audio id="myAudio" controls autoplay style="width: 100%;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Votre navigateur ne supporte pas l'élément audio.
    </audio>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var audio = document.getElementById('myAudio');
            audio.play().catch(function(error) {{
                console.log('Lecture automatique bloquée: ', error);
            }});
        }});
    </script>
    """

def transcrire_audio(audio_bytes):
    """Transcrit l’audio en texte avec SpeechRecognition ou Whisper."""
    if SR_AVAILABLE:
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            fichier_temp = f.name
        try:
            with sr.AudioFile(fichier_temp) as source:
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
            texte = recognizer.recognize_google(audio_data, language="fr-FR")
            return texte
        except sr.UnknownValueError:
            return "⚠️ Désolé, je n’ai pas compris."
        except sr.RequestError as e:
            return f"❌ Erreur du service Google : {e}"
        finally:
            os.unlink(fichier_temp)
    elif WHISPER_AVAILABLE:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            fichier_temp = f.name
        try:
            result = whisper_model.transcribe(fichier_temp, language="fr")
            return result["text"]
        except Exception as e:
            return f"❌ Erreur Whisper : {e}"
        finally:
            os.unlink(fichier_temp)
    else:
        return "❌ Aucun moteur de reconnaissance vocale disponible."

# ---------------- MAIN ----------------
def main():
    st.title("🎤 Assistant Vocal - Parlez & Écoutez")
    st.markdown("**Exprimez-vous vocalement et écoutez la réponse directement !**")

    if "audio_base64" not in st.session_state:
        st.session_state.audio_base64 = None
    if "audio_bytes" not in st.session_state:
        st.session_state.audio_bytes = None
    if "user_text" not in st.session_state:
        st.session_state.user_text = ""

    st.subheader("🎙️ Parlez maintenant :")
    audio = audiorecorder("Démarrer l'enregistrement", "Arrêter l'enregistrement")

    if audio is not None and hasattr(audio, "wav_data") and audio.wav_data is not None:
        audio_bytes = audio.wav_data  # ✅ Les vrais bytes WAV
        st.audio(audio_bytes, format="audio/wav")

        # Transcription
        user_text = transcrire_audio(audio_bytes)
        st.session_state.user_text = user_text
        st.success(f"🗣️ Vous avez dit : **{user_text}**")

        # Génération de la réponse
        response = f"Bonjour ! J’ai bien entendu : {user_text}. Comment puis-je vous aider aujourd’hui ?"
        st.subheader("🤖 Réponse :")
        st.info(response)

        # Génération audio réponse
        with st.spinner("🔄 Génération de la réponse audio..."):
            audio_base64, audio_bytes_mp3 = generate_audio_base64(response)
            if audio_base64:
                st.session_state.audio_base64 = audio_base64
                st.session_state.audio_bytes = audio_bytes_mp3
                st.success("✅ Audio généré ! Écoutez ci-dessous ↓")
                st.components.v1.html(audio_player_with_autoplay(audio_base64), height=80)
                st.audio(audio_bytes_mp3, format="audio/mp3")

    if st.session_state.audio_base64:
        st.markdown("---")
        st.subheader("🎵 Réécouter la dernière réponse")
        st.components.v1.html(audio_player_with_autoplay(st.session_state.audio_base64), height=80)
        st.download_button(
            label="📥 Télécharger la réponse audio",
            data=st.session_state.audio_bytes,
            file_name="reponse_assistant.mp3",
            mime="audio/mp3"
        )

if __name__ == "__main__":
    main()
