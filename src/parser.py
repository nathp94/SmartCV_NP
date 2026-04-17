import fitz  # PyMuPDF
import os

# ---------------------------------------------------------------------------
# EXTRACTION DU PDF EN JSON
# ---------------------------------------------------------------------------
def extract_text_from_pdf(pdf_path):

    if not os.path.exists(pdf_path):
        print(f"[ERREUR] Le fichier n'existe pas : {pdf_path}")
        return ""

    try:
        doc = fitz.open(pdf_path)
        full_text = ""

        for page in doc:
            full_text += page.get_text()

        # --- Nettoyage ---

        # 1. Normalisation des espaces et sauts de ligne
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        cleaned_text = "\n".join(lines)

        # 2. Encodage UTF-8 (pour éviter les caractères fantômes)
        cleaned_text = cleaned_text.encode("utf-8", "ignore").decode("utf-8")

        doc.close()
        return cleaned_text

    except Exception as e:
        print(f"[ERREUR] Échec du parsing PDF ({pdf_path}) : {e}")
        return ""

