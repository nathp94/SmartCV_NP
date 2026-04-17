# 🤖 SmartCV_NP

Assistant 100% local intelligent pour la génération et l'analyse de CV.

## 🌟 Fonctionnalités
- **✍️ Créateur de CV** : Transforme des notes brutes en un profil professionnel structuré (Markdown & JSON).
- **🔍 Analyseur de CV** : Audit complet d'un PDF (Score, Points forts, Points à améliorer) avec ou sans fiche de poste cible.
- **🌍 Multilingue** : Support complet du Français et de l'Anglais.
- **🔒 Confidentialité** : Aucun transfert de données vers le cloud (Propulsé par Ollama).

---

## 🚀 Installation & Exécution

### 1. Prérequis
- **Python 3.10+**
- **Ollama** : [Télécharger ici](https://ollama.com/)

### 2. Configuration de l'IA
Lancez Ollama et téléchargez le modèle requis :
```bash
ollama pull llama3.2:3b
```


### 3. Installation du projet
```bash
# Cloner le projet ou extraire l'archive
cd cv_ai_assistant

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Lancement
```bash
streamlit run app.py
```

---

## 🛠️ Détails Techniques

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Interface** | Streamlit | UI réactive et gestion d'état |
| **Modèle LLM** | Llama 3.2 (3B) | Inférence locale via Ollama |
| **Parsing PDF** | PyMuPDF (fitz) | Extraction et nettoyage du texte brut |
| **Pipeline** | Two-Step Chain | 1. Structuration brute -> 2. Analyse/Génération |
| **Formatage** | Markdown | Rendu dynamique et export léger |

---

## ⚠️ Limites et Hypothèses

- Matériel : Nécessite au moins 8 Go de RAM pour une fluidité correcte du modèle 3B.

- Parsing : L'outil extrait le texte textuel. Les CV sous forme d'images (scans) sans couche OCR ne sont pas supportés.

- Modèle 3B : Bien que performant, le modèle 3B peut parfois nécessiter un "Reset" si le JSON de sortie est mal formé malgré nos filtres de nettoyage.

- Performance : Puisqu'il s'agit d'un projet local à partir de LLM open-source, on assume une baisse de précision complexe au profit d'une inférence locale rapide et confidentielle.

---

## Crédits
- **Développeur** : Nathan Pégé
- **Projet** : SmartCV_NP (2026)
