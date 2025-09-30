import streamlit as st
import os
import re
from dotenv import load_dotenv, find_dotenv
import requests
#import uuid
import time
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
from gtts import gTTS
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import random


import streamlit as st
import requests
import io
import base64
import json
import random


# --- Fonctions utilitaires audio/langue ---

def detecter_langue(texte):
    """Détecte la langue du texte de manière robuste."""
    try:
        DetectorFactory.seed = 0
        texte_propre = re.sub(r'[^\w\s]', '', texte.strip())
        if len(texte_propre.split()) < 2:
            return "fr"
        langue = detect(texte_propre)
        return langue
    except LangDetectException:
        return "fr"
    except Exception:
        return "fr"

def parlers(texte, langue="auto"):
    """Synthèse vocale avec détection automatique de la langue et lecture audio."""
    try:
        if langue == "auto":
            langue_detectee = detecter_langue(texte)
        else:
            langue_detectee = langue
        mapping_langues = {
            'fr': 'fr', 'en': 'en', 'es': 'es', 'de': 'de', 'it': 'it', 'pt': 'pt', 'ru': 'ru', 'ja': 'ja',
            'zh-cn': 'zh', 'zh-tw': 'zh-tw', 'ko': 'ko', 'ar': 'ar', 'hi': 'hi', 'nl': 'nl', 'sv': 'sv',
            'da': 'da', 'no': 'no', 'fi': 'fi', 'el': 'el', 'tr': 'tr', 'pl': 'pl', 'uk': 'uk'
        }
        langue_finale = mapping_langues.get(langue_detectee, langue_detectee)
        tts = gTTS(text=texte, lang=langue_finale, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            temp_filename = tmp_file.name
        tts.save(temp_filename)
        os.system(f"afplay {temp_filename}")  # macOS
        os.unlink(temp_filename)
    except Exception as e:
        print(f"Erreur lors de la synthèse vocale: {e}")

def chat_interactif(consignes, modele, point_ia, point_user):
    """Boucle de dialogue interactif affichant tout l'historique."""
    st.session_state.setdefault("chat_history", [])
    st.info(f"L'IA défend le point de vue : **{point_ia}**\n\nVous défendez : **{point_user}**")
    st.markdown("---")
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"**Vous :** {msg['content']}")
        else:
            st.markdown(f"**IA :** {msg['content']}")
    st.markdown("---")
    # Saisie utilisateur (texte ou micro)
    user_input = st.text_input("Exprimez-vous ou cliquez sur le micro pour parler :", key="chat_input")
    # Remplace le bouton "Parler" par "Envoyer"
    if st.button("📤 Envoyer", key="btn_envoyer"):
        if user_input:
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            # Prépare la consigne pour l'IA
            consigne_ia = (
                f"Tu es un professeur qui défend le point de vue suivant : {point_ia}.\n"
                f"L'utilisateur défend ce point de vue : {point_user}.\n"
                f"Réponds brièvement (3-4 phrases max, 250 mots max), en restant courtois et en argumentant uniquement pour ton point de vue.\n"
                "Evite les répétitions inutiles et d'être redondant ou même hors sujet et vague.\n"
                "Donne des exemples concrets et pertinents pour illustrer tes arguments.\n"
                f"Ne change jamais de position, même si l'utilisateur insiste.\n"
                "Si le point de vue de l'utilisateur est valide, reconnais-le brièvement mais réaffirme ton propre point de vue.\n"
                "Si l'utilisateur dévie du sujet, ramène-le poliment à la question principale.\n"
                f"Réponds dans la langue du débat."
                f"Si l'utilisateur s'exprime dans une autre langue differente de celle du débat, réponds dans la langue du débat que tu ne comprends pas ce qu'il dit et ramene le dans la langue du débat."
            )
            # Appel du modèle
            reponse_ia = reponse(consigne_ia, user_input)
            st.session_state["chat_history"].append({"role": "ia", "content": reponse_ia})
            parler(reponse_ia)
            st.rerun()

def detecter_langue_simple(texte):
    """
    Détection avancée de langue avec support de 33 langues
    """
    if not texte or not texte.strip():
        return "fr"  # Par défaut français
    
    texte_lower = texte.lower()
    
    # Mots caractéristiques pour chaque langue (avec accents)
    mots_par_langue = {
        "fr": ["le", "la", "de", "et", "est", "que", "dans", "pour", "sur", "bonjour", "merci", 
               "avec", "son", "ses", "mais", "où", "donc", "car", "ni", "ou", "je", "tu", "il"],
        
        "en": ["the", "and", "is", "are", "for", "with", "this", "that", "hello", "thank", 
               "you", "we", "they", "what", "when", "where", "why", "how", "which", "who"],
        
        "es": ["el", "la", "de", "y", "en", "que", "por", "con", "hola", "gracias", 
               "los", "las", "un", "una", "del", "al", "se", "no", "si", "pero"],
        
        "de": ["der", "die", "das", "und", "ist", "sind", "für", "mit", "hallo", "danke",
               "ein", "eine", "den", "dem", "des", "zu", "von", "auf", "aus", "durch"],
        
        "it": ["il", "la", "di", "e", "è", "che", "in", "per", "con", "ciao", "grazie",
               "un", "una", "del", "al", "dal", "nel", "sul", "non", "ma", "o"],
        
        "pt": ["o", "a", "de", "e", "é", "que", "em", "para", "com", "olá", "obrigado",
               "um", "uma", "do", "da", "no", "na", "se", "não", "mas", "ou"],
        
        "ar": ["ال", "و", "في", "من", "إلى", "على", "أن", "هذا", "هذه", "مرحبا", "شكرا"],
        
        "zh": ["的", "是", "在", "和", "了", "有", "我", "你", "他", "我们", "你好", "谢谢"],
        
        "ja": ["の", "は", "に", "を", "が", "で", "と", "も", "です", "ます", "こんにちは", "ありがとう"],
        
        "ru": ["и", "в", "не", "на", "я", "он", "что", "это", "с", "по", "привет", "спасибо"],
        
        "nl": ["de", "het", "en", "is", "van", "een", "voor", "met", "hallo", "dank", 
               "je", "we", "ze", "er", "om", "maar", "of", "dan", "ook", "al"],
        
        "el": ["και", "το", "της", "του", "να", "ειναι", "για", "σε", "γεια", "ευχαριστω",
               "ο", "η", "τα", "με", "απο", "πως", "που", "αυτο", "αυτη", "αυτα"],
        
        "la": ["et", "in", "non", "est", "sed", "ad", "ex", "cum", "salve", "gratias",
               "quod", "qui", "quae", "quo", "ab", "de", "per", "pro", "sine", "sub"],
        
        "tr": ["ve", "bir", "bu", "şey", "için", "ile", "ama", "değil", "merhaba", "teşekkür",
               "ben", "sen", "o", "biz", "siz", "onlar", "ne", "nasıl", "niçin", "nerede"],
        
        "pl": ["i", "w", "nie", "się", "na", "jest", "dla", "z", "cześć", "dziękuję",
               "to", "co", "jak", "że", "po", "od", "do", "przez", "o", "za"],
        
        "sv": ["och", "i", "att", "är", "för", "med", "en", "ett", "hej", "tack",
               "det", "som", "av", "på", "vi", "de", "har", "inte", "om", "men"],
        
        "da": ["og", "i", "at", "er", "for", "med", "en", "et", "hej", "tak",
               "det", "som", "af", "på", "vi", "de", "har", "ikke", "om", "men"],
        
        "fi": ["ja", "on", "ei", "se", "että", "mutta", "kun", "niin", "hei", "kiitos",
               "minä", "sinä", "hän", "me", "te", "he", "tämä", "tuo", "nämä", "nuo"],
        
        "no": ["og", "i", "er", "for", "med", "en", "et", "hei", "takk", "det",
               "som", "av", "på", "vi", "de", "har", "ikke", "om", "men", "eller"],
        
        "ko": ["와", "과", "이", "가", "은", "는", "을", "를", "안녕", "감사", "합니다",
               "나는", "너는", "그는", "우리는", "그들은", "무엇", "어떻게", "왜", "어디"],
        
        "hi": ["और", "में", "है", "के", "लिए", "साथ", "एक", "नमस्ते", "धन्यवाद", "मैं",
               "तुम", "वह", "हम", "वे", "क्या", "कैसे", "क्यों", "कहाँ", "जो", "यह"],
        
        "vi": ["và", "trong", "là", "của", "cho", "với", "một", "xin chào", "cảm ơn", "tôi",
               "bạn", "anh", "chị", "chúng tôi", "họ", "gì", "như thế nào", "tại sao", "ở đâu"],
        
        "th": ["และ", "ใน", "คือ", "ของ", "เพื่อ", "กับ", "สวัสดี", "ขอบคุณ", "ฉัน", "คุณ",
               "เขา", "เรา", "พวกเขา", "อะไร", "อย่างไร", "ทำไม", "ที่ไหน", "ซึ่ง", "นี้"],
        
        "ro": ["și", "în", "este", "pentru", "cu", "un", "o", "salut", "mulțumesc", "eu",
               "tu", "el", "ea", "noi", "voi", "ei", "ce", "cum", "de ce", "unde"],
        
        "cs": ["a", "v", "je", "pro", "s", "se", "ahoj", "děkuji", "já", "ty",
               "on", "ona", "my", "vy", "oni", "co", "jak", "proč", "kde", "který"],
        
        "hu": ["és", "a", "az", "van", "nem", "hogy", "egy", "szia", "köszönöm", "én",
               "te", "ő", "mi", "ti", "ők", "mi", "hogyan", "miért", "hol", "ami"],
        
        "sr": ["и", "у", "је", "за", "са", "здраво", "хвала", "ја", "ти", "он",
               "она", "ми", "ви", "они", "шта", "како", "зашто", "где", "који"],
        
        "hr": ["i", "u", "je", "za", "s", "bok", "hvala", "ja", "ti", "on",
               "ona", "mi", "vi", "oni", "što", "kako", "zašto", "gdje", "koji"],
        
        "sk": ["a", "v", "je", "pre", "s", "ahoj", "ďakujem", "ja", "ty", "on",
               "ona", "my", "vy", "oni", "čo", "ako", "prečo", "kde", "ktorý"],
        
        "bg": ["и", "в", "е", "за", "с", "здравей", "благодаря", "аз", "ти", "той",
               "тя", "ние", "вие", "те", "какво", "как", "защо", "къде", "който"],
        
        "uk": ["і", "в", "не", "на", "я", "це", "що", "для", "з", "привіт", "дякую",
               "ти", "він", "вона", "ми", "ви", "вони", "що", "як", "чому", "де"],
        
        "fa": ["و", "در", "است", "برای", "با", "یک", "سلام", "متشکرم", "من", "تو",
               "او", "ما", "شما", "آنها", "چه", "چگونه", "چرا", "کجا", "که"],
        
        "he": ["ו", "ב", "את", "הוא", "היא", "זה", "זו", "של", "עם", "שלום", "תודה",
               "אני", "אתה", "את", "אנחנו", "אתם", "הם", "מה", "איך", "למה", "איפה"]
    }
    
    # Compter les occurrences pour chaque langue
    scores = {}
    for langue, mots in mots_par_langue.items():
        score = sum(1 for mot in mots if mot in texte_lower)
        scores[langue] = score
    
    # Trouver la langue avec le score le plus élevé
    langue_detectee = max(scores, key=scores.get)
    score_max = scores[langue_detectee]
    
    # Si le score est trop faible, utiliser la langue par défaut
    if score_max < 1:
        return "fr"
    
    return langue_detectee

def generer_reponse_intelligente(message_utilisateur, point_ia, point_user, langue_du_texte):
    """Génère des réponses contextuelles intelligentes"""
    
    #langue = detecter_langue_simple(message_utilisateur)

    st.session_state["chat_history"].append({"role": "user", "content": message_utilisateur})
    # Prépare la consigne pour l'IA
    consigne_ia = (
        f"Tu es un professeur qui défend le point de vue suivant : {point_ia} dans {langue_du_texte}.\n"
        f"L'utilisateur défend ce point de vue : {message_utilisateur}.\n"
        f"Réponds brièvement (3-4 phrases max, 250 mots max), en restant courtois et en argumentant uniquement pour ton point de vue.\n"
        "Evite les répétitions inutiles et d'être redondant ou même hors sujet et vague.\n"
        "Donne des exemples concrets et pertinents pour illustrer tes arguments.\n"
        f"Ne change jamais de position, même si l'utilisateur insiste.\n"
        "Si le point de vue de l'utilisateur est valide, reconnais-le brièvement mais réaffirme ton propre point de vue.\n"
        "Si l'utilisateur dévie du sujet, ramène-le poliment à la question principale.\n"
        f"Réponds dans la langue du débat."
        f"Si l'utilisateur s'exprime dans une autre langue differente de celle du débat, réponds dans la langue du débat que tu ne comprends pas ce qu'il dit et ramene le dans la langue du débat."
    )
    # Appel du modèle
    reponse_ia = reponse(consigne_ia, message_utilisateur)
    #parler(reponse_ia)
    #st.rerun()
    return reponse_ia


def compute_global_score(correction_text):
    details = []
    total = 0.0
    maxi = 0.0
    current_q = None
    num_questions = 0
    num_correct = 0
    for line in correction_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.lower().startswith("question:"):
            current_q = s
            num_questions += 1
        m = re.search(r"Note\s*:\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", s)
        if m:
            pts = float(m.group(1))
            mx = float(m.group(2))
            total += pts
            maxi += mx
            details.append({"question": current_q or "Question", "points": f"{pts}/{mx}"})
            if mx > 0 and abs(pts - mx) < 1e-6:
                num_correct += 1
    pourcentage_points = round(100.0 * total / maxi, 1) if maxi > 0 else 0.0
    percent_correct = round(100.0 * num_correct / num_questions, 1) if num_questions > 0 else 0.0
    appreciation = (
        "Excellent" if pourcentage_points >= 85 else
        "Très bien" if pourcentage_points >= 75 else
        "Bien" if pourcentage_points >= 65 else
        "Assez bien" if pourcentage_points >= 55 else
        "Passable" if pourcentage_points >= 50 else
        "Insuffisant"
    )
    return {
        "total_points_obtenus": int(total) if float(total).is_integer() else round(total, 2),
        "total_points_max": int(maxi) if float(maxi).is_integer() else round(maxi, 2),
        "pourcentage": pourcentage_points,
        "num_questions": num_questions,
        "num_correct": num_correct,
        "percent_correct": percent_correct,
        "appreciation": appreciation,
        "details": details,
    }

def correct_with_model(user_answers, langue_parlee):
    # Ne récupère plus le texte PDF ici !
    # texte_pdf = st.session_state.get("source_pdf_text", "")
    generated_text = st.session_state.get("exercice_genere", "")
    answers = st.session_state.get("answers", {})
    answers=user_answers
    if not generated_text or not answers:
        st.error("Données insuffisantes pour corriger.")
        return

    consignes = (
        "Tu es un correcteur d'examen de langue. Voici l'énoncé et les questions QCM suivies des réponses de l'élève.\n"
        "Corrige chaque question en indiquant la bonne réponse (A, B, C ou D), puis indique si la réponse de l'élève est correcte ou non.\n"
        "Fait attention, et n'oublie pas de strictement et formellement mentionner la réponse donnée par l'élève.\n"
        "Respecte strictement et formellement le format suivant pour chaque question :\n"
        "Respecte strictement et formellement les retours à la ligne.\n"
        "Format attendu :\n"
        "Question: [Numero de la question et ensuite Question]\n"
        f"Tu dois dire Réponse correcte : [A/B/C/D] en {langue_parlee} \n"
        f"Tu dois dire Réponse élève : [A/B/C/D ou texte] en {langue_parlee} \n"
        f"Résultat : [Correct/Incorrect en {langue_parlee}, avec explication de la réponse en 2-4 phrases dans {langue_parlee}]\n"
        "Note: 0/1\n"
        "(Répéter pour chaque question)\n"
    )
    prompt = (
        "EXERCICES GÉNÉRÉS:\n" + generated_text + "\n\n" +
        "RÉPONSES ÉTUDIANT (clé -> réponse):\n" + str(answers)
    )
    #st.write(generated_text)
    with st.spinner("Correction en cours..."):
        result = reponse(consignes, prompt)
    if result:
        st.subheader("📘 Correction détaillée")
        st.markdown(result)
        st.session_state["corrected_report"] = result
        st.subheader("🏁 Synthèse et Note Globale")
        synthese = compute_global_score(result)
        #st.write(synthese)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Réponses justes", f"{synthese['num_correct']} / {synthese['total_points_max']}")
        with col2:
            st.metric("% réponses justes", f"{synthese['pourcentage']}%")
        with col3:
            st.metric("Score points", f"{synthese['total_points_obtenus']} / {synthese['total_points_max']}")
        with col4:
            st.metric("Mention", synthese['appreciation'])
        with st.expander("Détails de la notation par question"):
            for item in synthese["details"]:
                st.write(f"- {item['question']} → {item['points']} pt(s)")
    else:
        st.error("La correction n'a pas pu être générée.")
        st.write("Debug - Résultat IA :", result)


# Place les fonctions ici, juste après les imports
def recupere_texte(exercice_genere):
    blocs = [b for b in exercice_genere.split("\n\n") if b.strip()]
    texte_blobs = []
    for bloc in blocs:
        if re.match(r"^1\s*\.", bloc.strip()):
            break
        texte_blobs.append(bloc)
    return "\n\n".join(texte_blobs)

def questions(exercice_genere):
    blocs = [b for b in exercice_genere.split("\n\n") if b.strip()]
    question_blobs = []
    i = 0
    while i < len(blocs):
        bloc = blocs[i]
        if re.match(r"^\d+\s*\.", bloc.strip()):
            question = bloc
            options = []
            j = i + 1
            while j < len(blocs) and not re.match(r"^\d+\s*\.", blocs[j].strip()):
                options.append(blocs[j])
                j += 1
            bloc_complet = question + "\n" + "\n".join(options)
            question_blobs.append(bloc_complet)
            i = j
        else:
            i += 1
    return question_blobs

env_path = find_dotenv(filename=".env", usecwd=True)
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv('OPENROUTER_API_KEY')
modele = "x-ai/grok-4-fast:free"


def reponse(consignes, texte):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8888/",
        "Content-Type": "application/json"
    }
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": modele,
        "messages": [
            {"role": "system", "content": consignes},
            {"role": "user", "content": texte}
        ]
    }
    response = requests.post(api_url, json=payload, headers=headers)
    response_json = response.json()
    resume = response_json['choices'][0]['message']['content']
    return resume


# Fonction pour générer l'exercice
def generer_exercice(langue, niveau, type_exercice):
    """
    Génère un exercice selon la langue, le niveau et le type d'exercice choisi.
    Stocke le résultat dans st.session_state.exercice_genere.
    """
    if not langue or not niveau:
        st.warning("Veuillez saisir la langue et le niveau.")
        return

    consignes = ""
    if type_exercice == "Grammaire":
        consignes = (
            "Respecte FORMELLEMENT ET STRICTEMENT le format demandé.\n\n"
            "Va sur des themes varies et actuels, pas des sujets classiques.\n\n"
            "Finance, technologie, environnement, société, culture, science, santé, éducation, voyages, etc.\n\n"
            f"Tu es un enseignant de {langue} et tu donnes cours à des élèves de niveau {niveau}.\n"
            f"À partir du texte fourni, génère EXCLUSIVEMENT des exercices de grammaire sous forme de phrases à compléter, "
            f"parfaitement adaptées au niveau {niveau}, et prêtes à être utilisées dans un examen écrit.\n\n"
            "Les bonnes reponses doivent strictement et formellement etre uniformement repartir entre les lettres A, B, C et D (Evite de concentrer les bonnes reponses sur une meme lettre).\n"
            "### EXIGENCES SPÉCIFIQUES POUR LES QCM DE GRAMMAIRE ###\n"
            "• Produire exactement 20 questions QCM (pas plus, pas moins)\n"
            "• Chaque question doit être une phrase comportant un ou plusieurs espaces vides (___) à compléter\n"
            "• Les espaces doivent concerner un point de grammaire précis (conjugaison, accord, préposition, article, pronom, etc.)\n"
            "• Une seule question par bloc, numérotée clairement (1. 2. 3. ...)\n"
            "• Chaque option doit apparaître sur UNE LIGNE DISTINCTE (A), B), C), D))\n"
            "• AUCUN saut de ligne entre la phrase et les options\n"
            "• Saut de 2 lignes vides après la dernière option avant la question suivante\n"
            "• Alignement vertical parfait des options\n"
            "• Espacement uniforme pour une mise en page claire\n"
            "• Aucune réponse ou correction ne doit apparaître\n\n"
            "### FORMATAGE EXIGÉ ###\n"
            "[Numéro]. [Phrase avec espace(s) à compléter : « … ___ … »]\n"
            "A) [Option A]\n"
            "B) [Option B]\n"
            "C) [Option C]\n"
            "D) [Option D]\n"
            "(laisser 2 lignes vides)\n\n"
            "### RÈGLES COMMUNES ###\n"
            "• Ne pas inventer de contenu extérieur au texte fourni\n"
            f"• Les questions doivent rester adaptées au niveau {niveau}\n"
            "• Numérotation cohérente (1 à 20)\n"
            "• Options toujours listées de A) à D)\n"
            "• Style professionnel, clair et homogène\n\n"
            "### VALIDATION FINALE ###\n"
            "✓ Vérifier qu’il y a exactement 20 questions QCM\n"
            "✓ Vérifier qu’aucune réponse n’apparaît\n"
            "✓ Vérifier que chaque question et ses options respectent le formatage\n"
            "✓ Vérifier que l’espacement est régulier et lisible\n\n"
            "⚠️ GÉNÈRE UNIQUEMENT des QCM de grammaire sous forme de phrases à compléter, "
            "dans le format sans aucun ajout, commentaire ou explication supplémentaire."
        )

    elif type_exercice == "Vocabulaire":
        consignes = (
            "Va sur des themes varies et actuels, pas des sujets classiques.\n\n"
            "Finance, technologie, environnement, société, culture, science, santé, éducation, voyages, etc.\n\n"
            "Respecte FORMELLEMENT ET STRICTEMENT le format demandé.\n\n"
            f"Tu es un enseignant de {langue} et tu donnes cours à des élèves de niveau {niveau}.\n"
            f"À partir du texte fourni, génère EXCLUSIVEMENT des exercices de vocabulaire, "
            f"parfaitement adaptés à {niveau}, dans un format prêt à être utilisé dans un examen écrit.\n\n"
            "Les bonnes reponses doivent strictement et formellement etre uniformement repartir entre les lettres A, B, C et D (Evite de concentrer les bonnes reponses sur une meme lettre).\n"
            "### EXIGENCES SPÉCIFIQUES POUR QCM DE VOCABULAIRE ###\n"
            "• Produire exactement 20 questions QCM (pas plus, pas moins)\n"
            "• Chaque question doit être une phrase comportant un espace vide (___) à compléter avec le mot approprié\n"
            "• Les propositions doivent être cohérentes et toutes de même nature grammaticale (ex : 4 verbes, 4 adjectifs, 4 noms...)\n"
            "• Chaque question doit tenir sur une ou deux lignes maximum (jamais coupée en plein milieu)\n"
            "• Une seule question par bloc, numérotée clairement (1. 2. 3. ...)\n"
            "• Chaque option doit apparaître sur UNE LIGNE DISTINCTE (A), B), C), D))\n"
            "• AUCUN saut de ligne entre la question et les options\n"
            "• Saut de 2 lignes vides après la dernière option avant la question suivante\n"
            "• Alignement vertical parfait des options\n"
            "• Espacement uniforme pour une mise en page claire\n"
            "• Aucune réponse ou correction ne doit apparaître\n\n"
            "### FORMATAGE EXIGÉ ###\n"
            "[Numéro]. [Phrase avec espace vide ___]\n"
            "A) [Option A]\n"
            "B) [Option B]\n"
            "C) [Option C]\n"
            "D) [Option D]\n"
            "(laisser 2 lignes vides)\n\n"
            "### RÈGLES COMMUNES ###\n"
            "• Ne pas inventer de contenu extérieur au texte fourni\n"
            f"• Les questions doivent rester adaptées au niveau {niveau}\n"
            "• Numérotation cohérente (1 à 20)\n"
            "• Options toujours listées de A) à D)\n"
            "• Style professionnel et lisible\n\n"
            "### VALIDATION FINALE ###\n"
            "✓ Vérifier qu’il y a exactement 20 questions QCM\n"
            "✓ Vérifier qu’aucune réponse n’apparaît\n"
            "✓ Vérifier que chaque question et ses options respectent le formatage\n"
            "✓ Vérifier que l’espacement est régulier et lisible\n\n"
            "⚠️ GÉNÈRE UNIQUEMENT des QCM de vocabulaire dans le format indiqué ci-dessus, "
            "sans aucun ajout, commentaire ou explication supplémentaire."
        )

    elif type_exercice == "Etude de texte":
        consignes = (
            "Va sur des themes varies et actuels, pas des sujets classiques.\n\n"
            "Finance, technologie, environnement, société, culture, science, santé, éducation, voyages, art, etc.\n\n"
            "Respecte FORMELLEMENT ET STRICTEMENT le format demandé.\n\n"
            f"Tu es un enseignant de {langue} et tu donnes cours à des élèves de niveau {niveau}.\n"
            f"Ton rôle est de créer un exercice complet d’étude de texte, de type Etude de texte, "
            f"similaire à ceux que l’on trouve dans des tests de langue officiels.\n\n"
            "Les bonnes reponses doivent strictement et formellement etre uniformement repartir entre les lettres A, B, C et D (Evite de concentrer les bonnes reponses sur une meme lettre).\n"
            "### ÉTAPE 1 : TEXTE DE RÉFÉRENCE ###\n"
            "• Générer un texte original, clair et authentique, parfaitement adapté au niveau indiqué.\n"
            "• Le texte doit avoir une longueur comprise entre 400 et 600 mots.\n"
            "• Le contenu doit être réaliste et cohérent (article, récit, dialogue, extrait d’essai, annonce, etc.), selon les pratiques des examens de langue.\n"
            "• La langue du texte doit correspondre à la matière choisie.\n\n"
            "• Fait en un seul paragraphe, soit en plusieurs paragraphes courts (3 à 5 lignes chacun) pour faciliter la lecture.\n"
            "• Ensuite tu produis un questionnaire de 20 questions QCM basées sur ce texte.\n\n"
            "### ÉTAPE 2 : QCM D’ÉTUDE DE TEXTE ###\n"
            "• Produire exactement 20 questions QCM (pas plus, pas moins).\n"
            "• Les questions doivent porter sur : compréhension globale, compréhension fine, vocabulaire en contexte, structure de phrases, intention de l’auteur, références implicites, etc.\n"
            "• Chaque question doit être concise (1 à 2 lignes maximum).\n"
            "• Une seule question par bloc, numérotée clairement (1. 2. 3. ...).\n"
            "• Chaque option doit apparaître sur UNE LIGNE DISTINCTE (A), B), C), D)).\n"
            "• Saut de ligne entre la question et les options.\n"
            "• Saut de 2 lignes vides après la dernière option avant la question suivante.\n"
            "• Alignement vertical parfait des options.\n"
            "• Aucune réponse ou correction ne doit apparaître.\n\n"
            "### FORMATAGE EXIGÉ  A RESPECTER FORMELLEMENT ET STRICTEMENT ###\n"
            "[D’abord le TEXTE complet ou énoncé, puis les QCM selon le format suivant : A RESPECTER FORMELLEMENT ET STRICTEMENT]\n\n"
            "[Numéro]. [Question complète]\n"
            "(ligne vide)\n"
            "A) [Option A]\n"
            "B) [Option B]\n"
            "C) [Option C]\n"
            "D) [Option D]\n"
            "(laisser 2 lignes vides)\n\n"
            "### RÈGLES COMMUNES ###\n"
            "• Ne pas inventer de contenu qui ne soit pas lié au texte généré.\n"
            f"• Les questions doivent rester adaptées au niveau {niveau}.\n"
            "• Numérotation cohérente (1 à 20).\n"
            "• Options toujours listées de A) à D).\n"
            "• Style professionnel et lisible.\n\n"
            "### VALIDATION FINALE ###\n"
            "✓ Vérifier qu’il y a bien un TEXTE avant les questions.\n"
            "✓ Vérifier qu’il y a exactement 20 questions QCM.\n"
            "✓ Vérifier qu’aucune réponse n’apparaît.\n"
            "✓ Vérifier que chaque question et ses options respectent le formatage.\n"
            "✓ Vérifier que l’espacement est régulier et lisible.\n\n"
            "⚠️ GÉNÈRE UNIQUEMENT le TEXTE suivi des 20 QCM dans le format indiqué ci-dessus, sans aucun ajout, commentaire ou explication supplémentaire."
        )

    elif type_exercice == "Exercices de conjugaison":
        consignes = (
            "Va sur des themes varies et actuels, pas des sujets classiques.\n\n"
            "Finance, technologie, environnement, société, culture, science, santé, éducation, voyages, etc.\n\n"
            "Respecte FORMELLEMENT ET STRICTEMENT le format demandé.\n\n"
            f"Tu es un enseignant de {langue} pour des élèves de niveau {niveau}.\n"
            f"À partir du texte fourni, génère EXCLUSIVEMENT 20 exercices de conjugaison adaptés à {niveau}.\n"
            "Les bonnes reponses doivent strictement et formellement etre uniformement repartir entre les lettres A, B, C et D (Evite de concentrer les bonnes reponses sur une meme lettre).\n"
            "### EXIGENCES ###\n"
            "• 20 phrases avec un verbe à compléter « ___ »\n"
            "• 4 propositions par phrase (A, B, C, D)\n"
            "• Une seule réponse correcte (ne pas l'indiquer)\n"
            "• Formatage strict:\n"
            "[Numéro]. [Phrase avec ___]\n"
            "(ligne vide)\n"
            "A) [Option A]\n"
            "B) [Option B]\n"
            "C) [Option C]\n"
            "D) [Option D]\n"
            "(2 lignes vides)\n"
            "### RÈGLES ###\n"
            "• Utiliser uniquement le texte fourni\n"
            f"• Adapter au niveau {niveau}\n"
            "• Numérotation 1 à 20\n"
            "• Options toujours A) à D)\n"
            "⚠️ UNIQUEMENT les exercices sans commentaires."
        )

    elif type_exercice == "Dialogue interactif":
        consignes = (
            f"Tu es un enseignant de {langue} et tu donnes cours à des élèves de niveau {niveau}.\n"
            f"À partir du texte fourni, génère EXCLUSIVEMENT un texte complet dans la langue {langue}, "
            f"adapté au niveau {niveau}, avec un style clair, correct et professionnel.\n\n"
            "Va sur des themes varies et actuels, pas des sujets classiques.\n\n"
            "Finance, technologie, environnement, société, culture, science, santé, éducation, voyages, etc.\n\n"
            "### EXIGENCES PRINCIPALES ###\n"
            "• Générer uniquement du texte, sans QCM, exercices, commentaires ou explications\n"
            "• Le texte doit avoir une longueur comprise entre 200 et 300 mots.\n"
            "• Respecter la langue de la matière\n"
            f"• La profondeur du texte doit être adapté au niveau {niveau}\n"
            "• Style clair, grammaticalement correct, fluide et cohérent\n"
            "• Aucun contenu extérieur ou inventé n’est autorisé\n"
            "• Le texte doit pouvoir être utilisé directement dans un document pédagogique ou examen\n\n"
            "### FORMATAGE ###\n"
            "• Texte continu, structuré en paragraphes si nécessaire\n"
            "• Orthographe, ponctuation et grammaire irréprochables\n"
            "• Aucun titre, numéro, ou balise spéciale n’est nécessaire\n\n"
            "### VALIDATION FINALE ###\n"
            "✓ Vérifier que le texte est exclusivement dans la langue de la matière\n"
            "✓ Vérifier qu’il est adapté au niveau demandé\n"
            "✓ Vérifier qu’aucun élément supplémentaire n’apparaît\n\n"
            "⚠️ GÉNÈRE UNIQUEMENT du texte dans la langue de la matière, "
            "sans aucun ajout, commentaire, question ou explication supplémentaire."
        )

    if consignes:
        with st.spinner("Génération en cours..."):
            exercice = reponse(consignes, "")
        st.session_state.exercice_genere = exercice

# Utilisation :
# if st.button("Générer exercice"):
#     generer_exercice(langue, niveau, type_exercice)

import re

def parse_grammaire(text: str):
    """Parse les exercices de grammaire au format QCM."""
    questions = []
    current = None
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^\d+\.", s):
            if current:
                questions.append(current)
            current = {"question": s, "options": []}
        elif re.match(r"^[ABCD]\)", s):
            if current is not None:
                current["options"].append(s)
        else:
            if current is not None and current["options"]:
                current["options"][-1] += " " + s
            elif current is not None:
                current["question"] += " " + s
    if current:
        questions.append(current)
    return questions

def parse_vocabulaire(text: str):
    """Parse les exercices de vocabulaire au format QCM."""
    # Identique à grammaire, même format
    return parse_grammaire(text)

def parse_conjugaison(text: str):
    """Parse les exercices de conjugaison au format QCM."""
    # Identique à grammaire, même format
    return parse_grammaire(text)

def parse_etude_de_texte(text: str):
    """Parse les exercices d'étude de texte : extrait le texte puis les QCM."""
    blocs = [b for b in text.split("\n\n") if b.strip()]
    texte = ""
    questions = []
    # On suppose que le premier bloc est le texte, le reste les questions
    if blocs:
        texte = blocs[0]
        for bloc in blocs[1:]:
            lignes = [l for l in bloc.split("\n") if l.strip()]
            if not lignes:
                continue
            question = lignes[0]
            options = [l for l in lignes if l.strip().startswith(("A)", "B)", "C)", "D)"))]
            questions.append({"question": question, "options": options})
    return {"texte": texte, "questions": questions}

def parse_dialogue_interactif(text: str):
    """
    Parse le texte généré pour l'exercice 'Dialogue interactif'.
    Retourne le texte sous forme d'un seul bloc (tout le texte d'un coup).
    """
    # Nettoie les espaces superflus et retourne le texte complet
    return text.strip()

# --- Intégration dans render_interactive_exercises ---

# ...existing code...

def render_interactive_exercises(type_exercice, langue, niveau, langue_parlee):
    generated_text = st.session_state.get("exercice_genere", "")
    generated_type = type_exercice
    meta = {
        "matiere": langue,
        "niveau": niveau,
    }
    if not generated_text or not generated_type:
        st.info("Aucun exercice en mémoire. Générez d'abord un contenu.")
        st.write({
            "has_generated_text": bool(generated_text),
            "generated_type": generated_type,
        })
        return

    st.subheader("📝 Répondez aux exercices")
    st.caption(f"Type: {generated_type} — Matière: {meta.get('matiere','')} — Niveau: {meta.get('niveau','')}")

    # Initialisation des réponses
    if "answers" not in st.session_state:
        st.session_state.answers = {}

    # Grammaire, Vocabulaire, Conjugaison : QCM
    if generated_type in ["Grammaire", "Vocabulaire", "Exercices de conjugaison"]:
        items = parse_grammaire(generated_text)
        for idx, q in enumerate(items, 1):
            st.markdown(f"**{q['question']}**")
            key = f"qcm_{idx}"
            choice = st.radio("Votre réponse", options=["A", "B", "C", "D"], horizontal=True, key=key)
            st.session_state.answers[key] = choice
            with st.expander("Afficher les options"):
                for opt in q["options"]:
                    st.write(opt)
            st.markdown("---")
        # Correction : récupère toutes les réponses dans l'ordre
        if st.button("✅ Valider et corriger", key="btn_validate_correct"):
            user_answers = [st.session_state.answers.get(f"qcm_{i+1}", "") for i in range(len(items))]
            #st.write("Debug - Réponses utilisateur :", user_answers)
            #with st.spinner("Correction en cours..."):
            correction = correct_with_model(user_answers, langue_parlee) #corrige_exercice(generated_text, user_answers)
            #st.subheader("📘 Correction détaillée")
            #st.markdown(correction)


    # Etude de texte : affiche d'abord le texte puis les questions/options
    elif generated_type == "Etude de texte":
        texte = recupere_texte(generated_text)
        questions_list = questions(generated_text)
        st.markdown("**Texte :**")
        st.markdown(texte)
        st.markdown("---")
        for idx, bloc in enumerate(questions_list, 1):
            lignes = [l for l in bloc.split("\n") if l.strip()]
            question = lignes[0] if lignes else ""
            options = [l for l in lignes if l.strip().startswith(("A)", "B)", "C)", "D)"))]
            st.markdown(f"**{question}**")
            key = f"etude_{idx}"
            choice = st.radio("Votre réponse", options=["A", "B", "C", "D"], horizontal=True, key=key)
            st.session_state.answers[key] = choice
            with st.expander("Afficher les options"):
                for opt in options:
                    st.write(opt)
            st.markdown("---")
        # Correction : récupère toutes les réponses dans l'ordre
        if st.button("✅ Valider et corriger", key="btn_validate_correct"):
            user_answers = [st.session_state.answers.get(f"etude_{i+1}", "") for i in range(len(questions_list))]
            #with st.spinner("Correction en cours..."):
            correction = correct_with_model(user_answers, langue_parlee) #corrige_exercice(generated_text, user_answers)
            #st.subheader("📘 Correction détaillée")
            #st.markdown(correction)
            # Synthèse globale
     #       synthese = compute_global_score(correction)
      #      st.subheader("🏁 Synthèse et Note Globale")
       #     st.write(synthese["appreciation"])



    # Dialogue interactif
    if generated_type == "Dialogue interactif":
        st.markdown("**Texte généré :**")
        bloc = parse_dialogue_interactif(generated_text)
        st.markdown(bloc)
        if st.button("🚀 Démarrer le dialogue", key="btn_start_dialogue"):
            langue_du_texte = detecter_langue(bloc)
            consignes = (
                f"Lis le texte ci-dessous et propose 3 à 5 points de vue ou positions différentes que l'on peut avoir sur ce texte. "
                f"Pour chaque point de vue, donne une phrase courte et claire qui résume ce point de vue. "
                f"Retourne uniquement la liste des points de vue, sans explication ni commentaire. "
                f"RÉPONDS STRICTEMENT dans la langue suivante : {langue_du_texte}."
            )
            prompt = bloc
            with st.spinner("Analyse des points de vue en cours..."):
                result = reponse(consignes, prompt)
            points = [p.strip("-•1234567890. ") for p in result.split("\n") if p.strip()]
            st.session_state["points_vue"] = points
            st.session_state["dialogue_ready"] = True
            st.rerun()
        if st.session_state.get("dialogue_ready"):
            points = st.session_state.get("points_vue", [])
            if points:
                st.markdown("**Choisissez un point de vue à discuter, votre objectif sera de défendre ce point de vue :**")
                choix = st.radio("Points de vue proposés :", points, key="radio_points_vue")
                st.session_state.answers["point_de_vue"] = choix
                if st.button("🔥 Let's go", key="btn_lets_go"):
                    autres = [p for p in points if p != choix]
                    import random
                    if autres:
                        point_ia = random.choice(autres)
                    else:
                        point_ia = "Un autre point de vue"
                    st.session_state["point_ia"] = point_ia
                    st.session_state["point_user"] = choix
                    st.session_state["chat_history"] = []
                    st.session_state["chat_started"] = True
                    st.session_state["debat_started"] = True  # Active le mode débat vocal
                    st.rerun()
                    
                    
        ####################################################################################            ################################################
        if st.session_state.get("debat_started"):
            bloc = parse_dialogue_interactif(generated_text)
            langue_du_texte = detecter_langue(bloc)

            st.markdown("---")
            st.info(f"L'IA défend le point de vue : **{st.session_state['point_ia']}**\n\nVous défendez : **{st.session_state['point_user']}**")
            st.markdown("---")
            for msg in st.session_state.get("chat_history", []):
                if msg["role"] == "user":
                    st.markdown(f"**Vous :** {msg['content']}")
                elif msg["role"] == "ia" and not msg.get("audio_played", False):
                    # N'affiche pas le texte tant que l'audio n'est pas joué
                    continue
                else:
                    st.markdown(f"**IA :** {msg['content']}")
            user_input = st.text_input("Votre message :", key="chat_input")
            if st.button("📤 Envoyer", key="btn_envoyer"):
                if user_input:
                    st.session_state["chat_history"].append({"role": "user", "content": user_input})
                    # Génère la réponse IA
                    reponse_ia = generer_reponse_intelligente(
                        user_input,
                        st.session_state["point_ia"],
                        st.session_state["point_user"],
                        langue_du_texte
                    )
                    # Ajoute la réponse IA mais ne l'affiche pas encore
                    st.session_state["chat_history"].append({"role": "ia", "content": reponse_ia, "audio_played": False})
                    st.rerun()
            # Si une réponse IA attend d'être jouée
            if st.session_state.get("chat_history") and st.session_state["chat_history"][-1]["role"] == "ia" and not st.session_state["chat_history"][-1].get("audio_played", False):
                reponse_ia = st.session_state["chat_history"][-1]["content"]
                langue_ia = detecter_langue(reponse_ia)
                texte_audio = reponse_ia
                #if st.button("🔊 Écouter la réponse audio", key="btn_play_audio"):
                parlers(texte_audio, langue_ia)
                st.session_state["chat_history"][-1]["audio_played"] = True
                st.rerun()
        return

# ...existing code...
# ...existing code...
    # ... autres types (QCM, étude de texte, etc.) ...

# NE PAS exécuter le code Streamlit en dehors de main()
# Laisse juste les définitions de fonctions et imports en dehors

# Optionnel : retire le st.set_page_config ici, laisse-le dans app.py

def main():
    if "exercice_genere" not in st.session_state:
        st.session_state.exercice_genere = None

    st.title("Générateur d'exercices de langue")

    niveaux_scolaires = [
        "6e", "5e", "4e", "3e", "2nde", "1ère", "Terminale",
        "Licence 1", "Licence 2", "Licence 3",
        "Master 1", "Master 2", "Doctorat"
    ]
    langues_possibles = [
        "Français", "Anglais", "Espagnol", "Allemand", "Italien", "Portugais",
        "Arabe", "Chinois", "Japonais", "Russe", "Néerlandais", "Grec", "Latin",
        "Turc", "Polonais", "Suédois", "Danois", "Finnois", "Norvégien", "Coréen",
        "Hindi", "Vietnamien", "Thaï", "Roumain", "Tchèque", "Hongrois", "Serbe",
        "Croate", "Slovaque", "Bulgare", "Ukrainien", "Persan", "Hébreu"
    ]

    langue = st.selectbox("Choisissez la langue pour l'exercice :", langues_possibles, key="selectbox_langue")
    niveau = st.selectbox("Choisissez votre niveau scolaire ou universitaire :", niveaux_scolaires, key="selectbox_niveau")
    type_exercice = st.selectbox(
        "Choisissez le type d'exercice :",
        ("Grammaire", "Vocabulaire", "Etude de texte", "Exercices de conjugaison", "Dialogue interactif"),
        key="selectbox_type_exercice"
    )
    
    # Ajout du menu pour choisir la langue parlée par l'étudiant
    langue_parlee = st.selectbox(
        "Choisissez la langue parlée par l'étudiant :",
        langues_possibles,
        key="selectbox_langue_parlee"
    )

    # Bouton générer toujours visible
    if st.button("Générer exercice de langue"):
        generer_exercice(langue, niveau, type_exercice)

    # Affiche les exercices interactifs si générés
    if st.session_state.exercice_genere:
        # Passe les variables nécessaires à la fonction
        render_interactive_exercises(type_exercice, langue, niveau, langue_parlee)

    # Dialogue interactif : génération du texte + analyse des points de vue + discussion vocale
    

if __name__ == "__main__":
    main()
