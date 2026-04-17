# ---------------------------------------------------------------------------
# TRANSFORMATION DU JSON EN MARKDOWN
# ---------------------------------------------------------------------------

def cv_data_to_markdown(data: dict) -> str:
    if not data or "error" in data:
        return f"⚠️ Erreur : {data.get('error', 'Données invalides')}"

    lines = []


    identity = data.get("identity", {})
    name = f"{identity.get('first_name', '')} {identity.get('last_name', '')}".strip()
    if name:
        lines.append(f"# {name}")
    if identity.get("email") or identity.get("phone"):
        contact_parts = []
        if identity.get("email"):
            contact_parts.append(f"📧 {identity['email']}")
        if identity.get("phone"):
            contact_parts.append(f"📞 {identity['phone']}")
        lines.append("  |  ".join(contact_parts))
    lines.append("")


    if data.get("summary"):
        lines.append("---")
        lines.append(f"*{data['summary']}*")
        lines.append("")


    experiences = data.get("experience", [])
    if experiences:
        lines.append("## 💼 Expériences professionnelles")
        for exp in experiences:
            title = exp.get("title", "")
            company = exp.get("company", "")
            dates = exp.get("dates", "")
            header_parts = [f"**{title}**" if title else ""]
            if company:
                header_parts.append(f"*{company}*")
            if dates:
                header_parts.append(f"`{dates}`")
            lines.append("### " + "  —  ".join(p for p in header_parts if p))
            for bullet in exp.get("description", []):
                lines.append(f"- {bullet}")
            lines.append("")


    projects = data.get("projects", [])
    if projects:
        lines.append("## 🚀 Projets")
        for proj in projects:
            lines.append(f"### {proj.get('name', 'Projet')}")
            lines.append(proj.get("description", ""))
            lines.append("")


    skills = data.get("skills", {})
    if skills:
        lines.append("## 🛠️ Compétences")
        if skills.get("technical"):
            lines.append("**Techniques :** " + " · ".join(f"`{s}`" for s in skills["technical"]))
        if skills.get("soft"):
            lines.append("**Soft skills :** " + " · ".join(skills["soft"]))
        lines.append("")


    education = data.get("education", [])
    if education:
        lines.append("## 🎓 Formation")
        for edu in education:
            degree = edu.get("degree", "")
            school = edu.get("school", "")
            year = edu.get("year", "")
            parts = [f"**{degree}**" if degree else ""]
            if school:
                parts.append(f"*{school}*")
            if year:
                parts.append(f"`{year}`")
            lines.append("- " + "  —  ".join(p for p in parts if p))
        lines.append("")

    return "\n".join(lines)