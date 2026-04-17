from fpdf import FPDF
import os


class CVExporter(FPDF):
    def __init__(self, lang='FR'):
        super().__init__()
        self.lang = lang
        # Dictionnaire de traduction pour les sections
        self.titles = {
            'FR': {
                'summary': 'Résumé Professionnel',
                'exp': 'Expériences Professionnelles',
                'projects': 'Projets',
                'skills': 'Compétences',
                'tech': 'Techniques :',
                'soft': 'Soft Skills :',
                'edu': 'Formation'
            },
            'EN': {
                'summary': 'Professional Summary',
                'exp': 'Work Experience',
                'projects': 'Projects',
                'skills': 'Skills',
                'tech': 'Technical:',
                'soft': 'Soft Skills:',
                'edu': 'Education'
            }
        }

    def header(self):
        # Pas de header spécifique pour un CV, mais requis par FPDF
        pass

    def section_title(self, label):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, f"  {label}", ln=True, fill=True)
        self.ln(4)

    def safe_text(self, text):
        """Nettoie le texte pour l'encodage standard de FPDF"""
        if not text: return ""
        # Remplace les puces courantes et caractères spéciaux
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    def generate_pdf(self, data, output_path):
        self.add_page()
        t = self.titles[self.lang]

        # --- 1. IDENTITÉ ---
        id_data = data.get('identity', {})
        name = f"{id_data.get('first_name', '')} {id_data.get('last_name', '')}"
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 10, self.safe_text(name), ln=True)

        self.set_font('Helvetica', '', 11)
        contact = f"{id_data.get('email', '')} | {id_data.get('phone', '')}"
        self.cell(0, 10, self.safe_text(contact), ln=True)
        self.ln(5)

        # --- 2. RÉSUMÉ ---
        if data.get('summary'):
            self.section_title(t['summary'])
            self.set_font('Helvetica', '', 10)
            self.multi_cell(0, 5, self.safe_text(data['summary']))
            self.ln(5)

        # --- 3. EXPÉRIENCES ---
        if data.get('experience'):
            self.section_title(t['exp'])
            for exp in data['experience']:
                self.set_font('Helvetica', 'B', 11)
                title_line = f"{exp.get('title')} - {exp.get('company')}"
                date_line = f"({exp.get('dates')})"

                self.cell(140, 6, self.safe_text(title_line))
                self.set_font('Helvetica', 'I', 10)
                self.cell(0, 6, self.safe_text(date_line), ln=True, align='R')

                self.set_font('Helvetica', '', 10)
                desc = exp.get('description', '')
                if isinstance(desc, list):
                    for point in desc:
                        self.cell(5)  # Indentation
                        self.multi_cell(0, 5, self.safe_text(f"- {point}"))
                else:
                    self.multi_cell(0, 5, self.safe_text(desc))
                self.ln(3)

        # --- 4. COMPÉTENCES ---
        if data.get('skills'):
            self.section_title(t['skills'])
            skills = data['skills']
            self.set_font('Helvetica', 'B', 10)

            # Tech Skills
            if skills.get('technical'):
                self.write(5, self.safe_text(t['tech'] + " "))
                self.set_font('Helvetica', '', 10)
                self.multi_cell(0, 5, self.safe_text(", ".join(skills['technical'])))
                self.ln(2)

            # Soft Skills
            if skills.get('soft'):
                self.set_font('Helvetica', 'B', 10)
                self.write(5, self.safe_text(t['soft'] + " "))
                self.set_font('Helvetica', '', 10)
                self.multi_cell(0, 5, self.safe_text(", ".join(skills['soft'])))
                self.ln(5)

        # --- 5. EDUCATION ---
        if data.get('education'):
            self.section_title(t['edu'])
            for edu in data['education']:
                self.set_font('Helvetica', 'B', 11)
                self.cell(0, 6, self.safe_text(edu.get('degree')), ln=True)
                self.set_font('Helvetica', '', 10)
                school_line = f"{edu.get('school')} ({edu.get('year')})"
                self.cell(0, 6, self.safe_text(school_line), ln=True)
                self.ln(2)

        # Sauvegarde
        self.output(output_path)


def export_to_pdf(data, output_path, lang='FR'):
    """Fonction helper pour faciliter l'appel depuis l'App"""
    try:
        pdf = CVExporter(lang=lang)
        pdf.generate_pdf(data, output_path)
        return True
    except Exception as e:
        print(f"[ERREUR EXPORTER] : {e}")
        return False