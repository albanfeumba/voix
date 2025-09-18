import streamlit as st
import base64

def main():
    st.title("🎤 Assistant Simple")
    
    user_input = st.text_input("Tapez votre message:", "")
    
    if st.button("Envoyer") and user_input:
        st.write(f"**Vous avez dit:** {user_input}")
        st.write(f"**Réponse:** J'ai compris: {user_input}")
        
        # Option: lecture audio simple (nécessite navigateur)
        st.audio(f"data:audio/wav;base64,{base64.b64encode(b'audio_simule').decode()}")

if __name__ == "__main__":
    main()
