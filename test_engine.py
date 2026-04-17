from src.llm_logic import generate_cv_structure, analyze_cv_content
from src.parser import extract_text_from_pdf
from src.format import export_to_pdf
import json
import os

def test_generation_et_export():
    print("\n--- TEST : GÉNÉRATION & EXPORT PDF ---")

    parcours_vrac = """
    Je m'appelle Jean Dupont, mon mail est j.dupont@email.com, tel: 0601020304. 
    J'ai été Développeur Python chez TechCorp de 2020 à 2023 où j'ai créé des API FastAPI.
    Avant j'étais stagiaire chez DataSoft en 2019. 
    Je maîtrise Python, SQL et je parle anglais couramment.
    Diplômé de l'Efrei en 2020.
    """

    # 1. Appel au LLM
    print("[1/3] Envoi des notes au LLM (Llama 3.2 3B)...")
    result = generate_cv_structure(parcours_vrac)

    if result:
        print("[OK] JSON structuré reçu avec succès.")

        # 2. Préparation de l'export
        output_folder = "data"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_filename = os.path.join(output_folder, "test_export_cv.pdf")

        # 3. Génération du PDF
        print(f"[2/3] Génération du PDF dans : {output_filename}...")
        success = export_to_pdf(result, output_filename, lang='FR')

        if success:
            print(f"[3/3] [SUCCÈS] Le CV a été généré !")
            print(f"Vérifie le dossier '{output_folder}' pour voir le résultat.")
        else:
            print("[ERREUR] Échec de la création du fichier PDF.")
    else:
        print("[ERREUR] Échec de la génération de la structure par l'IA.")



def test_analyse():
    print("\n--- TEST 2 : ANALYSE DE CARRIÈRE ---")

    # Simule un texte extrait d'un PDF par ton parser
    cv_texte_extrait = "Jean Dupont. Développeur Python expert en backend et bases de données SQL."
    job_desc = "Recherchons un développeur Python Senior avec des compétences en Cloud (AWS) et API."

    print("Analyse de compatibilité en cours...")
    analyse = analyze_cv_content(cv_texte_extrait, job_desc)

    if analyse:
        print(f"Score : {analyse.get('score')}/100")
        print(f"Points forts : {analyse.get('strengths')}")
        print(f"Conseil : {analyse.get('global_advice')}")
    else:
        print("Échec de l'analyse.")



if __name__ == "__main__":
    test_generation_et_export()
    #test_analyse()
