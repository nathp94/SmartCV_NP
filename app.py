import streamlit as st
import os
import json
from src.parser import extract_text_from_pdf
from src.llm_logic import generate_cv_structure, analyze_cv_content
from src.format import cv_data_to_markdown

# Fichier app.py


# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="IA CV Assistant", page_icon="🤖", layout="wide")

# Initialisation du dossier data
if not os.path.exists("data"):
    os.makedirs("data")

# --- INITIALISATION DU SESSION STATE ---
if 'cv_data' not in st.session_state:
    st.session_state.cv_data = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# --- SIDEBAR & CONFIGURATION ---
with st.sidebar:
    st.title("🤖 IA CV Assistant")
    st.markdown("---")

    lang = st.radio("🌐 Langue / Language", ["FR", "EN"])

    st.markdown("---")
    st.info(f"**Modèle :** Llama 3.2 3B\n\n**Status :** Connecté ✅")

    if st.button("🔄 Réinitialiser / Reset"):
        st.session_state.cv_data = None
        st.session_state.analysis_result = None
        st.rerun()

# --- TRADUCTIONS ---
texts = {
    'FR': {
        'tab1': "✍️ Créateur", 'tab2': "🔍 Analyseur",
        'input_label': "Décrivez votre parcours (expériences, études, compétences) :",
        'btn_gen': "Générer mon CV", 'spinner_gen': "L'IA structure votre parcours...",
        'download_btn': "Télécharger mon CV (PDF)",
        'upload_label': "Uploadez votre CV (PDF)",
        'target_label': "Poste visé (Optionnel)",
        'btn_audit': "Lancer l'Audit", 'audit_spinner': "Analyse en cours...",
        'score': "Score de Match", 'strengths': "Points Forts",
        'weaknesses': "Points à Améliorer", 'advice': "Conseil Global"
    },
    'EN': {
        'tab1': "✍️ Builder", 'tab2': "🔍 Analyzer",
        'input_label': "Describe your background (experience, education, skills):",
        'btn_gen': "Generate my CV", 'spinner_gen': "AI is structuring your profile...",
        'download_btn': "Download my CV (PDF)",
        'upload_label': "Upload your CV (PDF)",
        'target_label': "Target Job Title (Optional)",
        'btn_audit': "Run Audit", 'audit_spinner': "Analyzing content...",
        'score': "Match Score", 'strengths': "Strengths",
        'weaknesses': "Areas for Improvement", 'advice': "Global Advice"
    }
}[lang]

tab1, tab2 = st.tabs([texts['tab1'], texts['tab2']])

# --- ONGLET 1 : CRÉATEUR DE CV ---
with tab1:
    user_input = st.text_area(texts['input_label'], height=250, placeholder="Ex: Je m'appelle Jean...")

    if st.button(texts['btn_gen'], type="primary"):
        if user_input.strip():
            with st.spinner(texts['spinner_gen']):
                st.session_state.cv_data = generate_cv_structure(user_input)
        else:
            st.warning("Veuillez saisir du texte.")

    if st.session_state.cv_data:
        st.success("✅ CV Généré avec succès !")

        tab_preview, tab_raw = st.tabs(["👁️ Aperçu CV", "🔧 JSON brut"])

        with tab_preview:
            md_content = cv_data_to_markdown(st.session_state.cv_data)
            st.markdown(md_content)
            st.download_button(
                label="⬇️ Télécharger en Markdown",
                data=md_content,
                file_name="mon_cv.md",
                mime="text/markdown"
            )

        with tab_raw:
            st.json(st.session_state.cv_data)

# --- ONGLET 2 : ANALYSEUR DE CV ---
with tab2:
    uploaded_file = st.file_uploader(texts['upload_label'], type="pdf")

    if st.button(texts['btn_audit'], type="primary"):
        if uploaded_file:
            # Sauvegarde temporaire du fichier
            temp_path = os.path.join("data", "temp_analysis.pdf")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner(texts['audit_spinner']):
                cv_text = extract_text_from_pdf(temp_path)
                if cv_text:
                    st.session_state.analysis_result = analyze_cv_content(cv_text)
                else:
                    st.error("Impossible de lire le PDF.")
        else:
            st.warning("Veuillez uploader un fichier PDF.")

    if st.session_state.analysis_result:
        res = st.session_state.analysis_result

        # Affichage du score
        score = res.get('score', 0)
        st.metric(label=texts['score'], value=f"{score}%")
        st.progress(score / 100)

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"✅ {texts['strengths']}")
            for s in res.get('strengths', []):
                st.write(f"- {s}")

        with col2:
            st.subheader(f"⚠️ {texts['weaknesses']}")
            for w in res.get('weaknesses', []):
                st.write(f"- {w}")

        st.markdown("---")
        st.subheader(f"💡 {texts['advice']}")
        st.info(res.get('global_advice', "Pas de conseil disponible."))