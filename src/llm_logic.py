import ollama
import re
import json
import os
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def clean_json_response(response_text: str) -> dict:
    """
    Extrait le bloc JSON d'une réponse textuelle à l'aide de Regex.
    """
    try:
        # Cherche le premier '{' et le dernier '}'
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        return {"error": "Aucun JSON trouvé dans la réponse"}
    except json.JSONDecodeError:
        return {"error": "Format JSON invalide"}

def call_local_llm(prompt: str, system_prompt: str):
    """
    Appel générique à l'instance locale Ollama.
    """
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        options={"temperature": 0.1}  # Température basse pour plus de rigueur
    )
    return response['message']['content']

def generate_cv_structure(user_input: str) -> dict:
    """
    Transforme un résumé de parcours en JSON structuré.
    """
    system_prompt = (
        "You are an HR Assistant. You must detect the language of the user input (French or English) "
        "and generate the CV content in that same language. However, JSON KEYS MUST ALWAYS BE IN ENGLISH.\n"
        "Format strictly as JSON with these keys: "
        "identity (obj: first_name, last_name, email, phone), "
        "summary (string), "
        "experience (list of objs: title, company, dates, description), "
        "projects (list of objs: name, description), "
        "skills (obj: technical: list, soft: list), "
        "education (list of objs: degree, school, year).\n"
        "Return ONLY the JSON. No conversational text."
    )

    raw_response = call_local_llm(user_input, system_prompt)
    return clean_json_response(raw_response)

def analyze_cv_content(cv_text: str) -> dict:
    """
    Analyse un CV par rapport à une fiche de poste.
    """
    system_prompt = (
        "Tu es un expert en recrutement. Analyse le CV fourni"
        "Réponds en JSON strict avec ces clés : score (0-100), strengths (liste), weaknesses (liste), global_advice (string). "
        "Réponds uniquement avec le JSON."
    ).replace("'", '"')

    prompt = f"CV TEXT:\n{cv_text}\n"
    raw_response = call_local_llm(prompt, system_prompt)
    return clean_json_response(raw_response)