import ollama
import re
import json
import os
from dotenv import load_dotenv

# fichier llm_logic.py

load_dotenv()
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


# ---------------------------------------------------------------------------
# UTILITAIRES JSON
# ---------------------------------------------------------------------------

def extract_json_block(text: str) -> str | None:
    """
    Extrait le premier bloc JSON valide en comptant les accolades.
    Plus robuste que le simple Regex `{.*}`.
    """
    start = text.find('{')
    if start == -1:
        return None

    depth = 0
    for i, char in enumerate(text[start:], start=start):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def clean_json_response(response_text: str) -> dict:
    """
    Tente d'extraire et de parser le JSON de la réponse LLM.
    Fallback sur le Regex simple si le comptage d'accolades échoue.
    """
    # Tentative 1 : comptage d'accolades (plus fiable)
    json_str = extract_json_block(response_text)

    # Tentative 2 : Regex classique en fallback
    if not json_str:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        json_str = match.group(0) if match else None

    if not json_str:
        return {"error": "Aucun JSON trouvé dans la réponse"}

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Tentative 3 : nettoyage des virgules trailing (erreur LLM courante)
        json_str_cleaned = re.sub(r',\s*([}\]])', r'\1', json_str)
        try:
            return json.loads(json_str_cleaned)
        except json.JSONDecodeError:
            return {"error": "Format JSON invalide malgré le nettoyage"}


# ---------------------------------------------------------------------------
# APPEL LLM GÉNÉRIQUE
# ---------------------------------------------------------------------------

def call_local_llm(prompt: str, system_prompt: str) -> str:
    """
    Appel générique à l'instance locale Ollama.
    """
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        options={"temperature": 0.1}
    )
    return response['message']['content']


# ---------------------------------------------------------------------------
# PIPELINE GÉNÉRATION CV — ÉTAPE 1 : ENRICHISSEMENT
# ---------------------------------------------------------------------------

def enrich_user_input(user_input: str) -> str:
    """
    Étape 1 : Le LLM interprète et enrichit le texte brut de l'utilisateur.
    Retourne un texte enrichi (pas encore du JSON).
    """
    system_prompt = (
        "You are a senior HR consultant and professional CV writer with 15 years of experience. "
        "Your role is to take a raw description of someone's career and enrich it into a detailed, "
        "professional profile ready to be formatted into a CV.\n\n"

        "RULES:\n"
        "- Detect the language of the input (French or English) and respond in THAT SAME language.\n"
        "- If the input is short or vague, intelligently infer plausible details "
        "(job titles, sector, key responsibilities) based on context clues. "
        "Mark inferred details clearly with [inferred].\n"
        "- Reformulate experiences using strong action verbs and professional vocabulary.\n"
        "- Write a value-oriented professional summary answering: "
        "'What unique value does this candidate bring?' (2-3 sentences max).\n"
        "- If the user mentions projects explicitly, include them. If not, do NOT invent any.\n"
        "- Expand on skills based on the mentioned experiences if they seem incomplete.\n"
        "- Output a structured plain text profile (no JSON yet), with clear sections: "
        "IDENTITY, SUMMARY, EXPERIENCE, SKILLS, EDUCATION, and optionally PROJECTS.\n"
        "- Do NOT add fictional companies or dates unless the user provided them."
    )

    prompt = (
        f"Here is the raw career description from the user:\n\n"
        f"---\n{user_input}\n---\n\n"
        f"Enrich this into a detailed professional profile."
    )

    return call_local_llm(prompt, system_prompt)


# ---------------------------------------------------------------------------
# PIPELINE GÉNÉRATION CV — ÉTAPE 2 : STRUCTURATION JSON
# ---------------------------------------------------------------------------

# Exemple injecté dans le prompt pour guider le LLM 3B
FEW_SHOT_EXAMPLE = """
{
  "identity": {
    "first_name": "Sophie",
    "last_name": "Martin",
    "email": "sophie.martin@email.com",
    "phone": "+33 6 12 34 56 78"
  },
  "summary": "Développeuse full-stack avec 5 ans d'expérience en environnements agiles, spécialisée dans la conception d'APIs performantes. Reconnue pour sa capacité à livrer des solutions robustes dans des délais serrés.",
  "experience": [
    {
      "title": "Développeuse Full-Stack",
      "company": "TechCorp",
      "dates": "2020 - 2024",
      "description": ["Conception et déploiement de 3 APIs REST en Python/FastAPI", "Réduction de 30% du temps de chargement des pages"]
    }
  ],
  "projects": [
    {
      "name": "Portfolio personnel",
      "description": "Site vitrine développé avec React et déployé sur Vercel"
    }
  ],
  "skills": {
    "technical": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
    "soft": ["Gestion de projet", "Communication", "Adaptabilité"]
  },
  "education": [
    {
      "degree": "Master Informatique",
      "school": "Université Paris-Saclay",
      "year": "2019"
    }
  ]
}
"""


def structure_to_json(enriched_profile: str) -> dict:
    """
    Étape 2 : Transforme le profil enrichi en JSON structuré strict.
    Utilise un exemple few-shot pour guider le LLM 3B.
    """
    system_prompt = (
        "You are a data formatting specialist. Your ONLY job is to convert a professional profile "
        "into a strictly valid JSON object. You must output ONLY the JSON — no explanations, "
        "no markdown, no preamble, no trailing text.\n\n"

        "JSON KEYS MUST ALWAYS BE IN ENGLISH.\n"
        "The VALUES must be in the same language as the input profile (French or English).\n\n"

        "REQUIRED STRUCTURE (follow exactly):\n"
        "- identity: object with first_name, last_name, email, phone\n"
        "If no identity mentionned, set random realistic informations"
        "- summary: string (2-3 sentences, value-oriented)\n"
        "- experience: list of objects with title, company, dates, description (list of strings)\n"
        "- projects: list of objects with name, description — ONLY if explicitly mentioned. "
        "If no projects were mentioned, set this to an empty list [].\n"
        "- skills: object with technical (list of strings) and soft (list of strings)\n"
        "- education: list of objects with degree, school, year\n\n"

        "Remove any [inferred] tags from the content.\n\n"

        f"EXAMPLE OF VALID OUTPUT:\n{FEW_SHOT_EXAMPLE}\n\n"
        "Now convert the profile below into the same JSON format."
    )

    prompt = (
        f"Professional profile to convert:\n\n"
        f"---\n{enriched_profile}\n---"
    )

    raw_response = call_local_llm(prompt, system_prompt)
    return clean_json_response(raw_response)


# ---------------------------------------------------------------------------
# FONCTION PRINCIPALE — PIPELINE COMPLET
# ---------------------------------------------------------------------------

def generate_cv_structure(user_input: str) -> dict:
    """
    Pipeline complet en 2 étapes :
    1. Enrichissement du texte brut
    2. Structuration en JSON strict
    """
    # Étape 1
    enriched_profile = enrich_user_input(user_input)

    # Étape 2
    cv_data = structure_to_json(enriched_profile)

    return cv_data


# ---------------------------------------------------------------------------
# ANALYSE DE CV (Onglet 2 )
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# PIPELINE ANALYSE — ÉTAPE 1 : NORMALISATION
# ---------------------------------------------------------------------------


def normalize_cv_structure(raw_text: str) -> str:
    """
    Étape 1 : Nettoie la structure du texte extrait du PDF sans modifier le contenu.
    Répare les sauts de ligne et regroupe les informations par blocs logiques.
    """
    system_prompt = (
        "You are a document restoration expert. Your goal is to take a messy text extraction from a PDF CV "
        "and reorganize it into clear, logical sections (Identity, Summary, Experience, Skills, Education).\n\n"
        "RULES:\n"
        "- KEEP THE EXACT ORIGINAL WORDS. Do NOT paraphrase or improve the text.\n"
        "- RESPOND IN THE SAME LANGUAGE AS THE INPUT TEXT (French or English).\n"
        "- Fix broken lines or words cut in half by the PDF extraction process.\n"
        "- Ensure dates are correctly attached to their respective job titles or schools.\n"
        "- Use clear headers for each section.\n"
        "- Remove any layout noise (page numbers, repeated headers/footers).\n"
    )

    prompt = f"Messy CV text to reorganize:\n\n---\n{raw_text}\n---"
    return call_local_llm(prompt, system_prompt)


# ---------------------------------------------------------------------------
# PIPELINE ANALYSE — ÉTAPE 2 : AUDIT RH
# ---------------------------------------------------------------------------

def audit_cv_quality(structured_text: str, target_job: str = "") -> dict:
    """
    Étape 2 : Expertise RH sur le texte normalisé.
    """
    job_context = (
        f"TARGET POSITION: {target_job}. Evaluate the CV specifically for this role."
        if target_job
        else "No specific job provided. Evaluate the general professional quality, impact, and clarity of the CV."
    )

    system_prompt = (
        "You are a Senior Recruitment Expert. Your role is to audit a structured CV profile.\n"
        f"CONTEXT: {job_context}\n\n"
        "CRITERIA:\n"
        "- RESPOND IN THE SAME LANGUAGE AS THE INPUT TEXT (French or English).\n"
        "- Use of action verbs and quantifiable results.\n"
        "- Clarity of the career path.\n"
        "- Technical relevance and skill density.\n\n"
        "JSON KEYS REQUIRED (Always in English):\n"
        "- score: Integer (0-100)\n"
        "- strengths: List of strings\n"
        "- weaknesses: List of strings\n"
        "- global_advice: A concise, actionable string advice.\n\n"
        "Return ONLY the JSON. No conversation."
    )

    prompt = f"STRUCTURED CV TEXT:\n{structured_text}\n"
    raw_response = call_local_llm(prompt, system_prompt)
    return clean_json_response(raw_response)


# ---------------------------------------------------------------------------
# FONCTION PRINCIPALE — ANALYSE COMPLÈTE
# ---------------------------------------------------------------------------

def analyze_cv_content(cv_text: str, target_job: str = "") -> dict:
    """
    Pipeline d'analyse en 2 étapes :
    1. Normalisation du texte brut
    2. Audit par l'expert IA
    """
    # Étape 1 : Nettoyage structurel
    normalized_text = normalize_cv_structure(cv_text)

    # Étape 2 : Analyse métier
    analysis = audit_cv_quality(normalized_text, target_job)

    return analysis