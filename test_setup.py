import ollama
from dotenv import load_dotenv
import os
import sys

load_dotenv()


def check_setup():
    print("--- Diagnostic du Setup AI CV ---")

    # 1. Check Python version
    print(f"[OK] Python {sys.version.split()[0]}")

    # 2. Check Ollama Connection
    model_name = os.getenv("OLLAMA_MODEL", "llama3")
    try:
        response = ollama.chat(model=model_name, messages=[
            {'role': 'user', 'content': 'Dis "Connexion OK" en deux mots.'}
        ])
        print(f"[OK] Ollama contacté (Modèle: {model_name})")
        print(f"     Réponse : {response['message']['content'].strip()}")
    except Exception as e:
        print(f"[ERREUR] Impossible de joindre Ollama: {e}")
        print("         Vérifie qu'Ollama est lancé et que le modèle soit pull.")


if __name__ == "__main__":
    check_setup()
