from typing import List, Optional
from .models import ModuleApprovalConfig

def get_module_config(module: str) -> Optional[ModuleApprovalConfig]:
    """Liefert die aktive Konfiguration für ein Modul oder None."""
    return ModuleApprovalConfig.objects.filter(module=module, is_active=True).first()

def recipients_list(cfg: Optional[ModuleApprovalConfig]) -> List[str]:
    """Semikolon-getrennte Empfänger in eine saubere Liste umwandeln."""
    if not cfg:
        return []
    raw = cfg.archive_recipients or ""
    return [p.strip() for p in raw.split(";") if p.strip()]

def build_archive_mail_preview(tr, sequence, cfg: Optional[ModuleApprovalConfig]) -> dict:
    """
    Baut einen Beispiel-Betreff/Text für die Abschlussmail (ohne Versand).
    """
    recipients = recipients_list(cfg)
    seq_str = " → ".join([f.name for f in sequence]) if sequence else "(keine)"
    subject = f"RKA #{tr.pk} – Abschluss & Ablage"
    body = (
        f"Reisekostenantrag #{tr.pk}\n"
        f"Antragsteller: {tr.applicant}\n"
        f"Genehmigungsreihenfolge: {seq_str}\n\n"
        f"Dies ist eine Vorschau. In der echten Ausführung würde hier die finale PDF angehängt "
        f"und an die unten stehenden Empfänger versendet."
    )
    return {"subject": subject, "body": body, "recipients": recipients}
