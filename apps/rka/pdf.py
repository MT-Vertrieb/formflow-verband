from io import BytesIO
from pathlib import Path
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def _safe_text(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _sig_image_or_none(user, max_w=35*mm, max_h=15*mm):
    """Versuche, eine Unterschriftsgrafik des Users einzubetten; sonst None."""
    try:
        prof = user.profile  # apps.accounts.models.Profile (OneToOne)
        if getattr(prof, "signature_image", None) and prof.signature_image.name:
            p = Path(prof.signature_image.path)
            if p.exists():
                img = Image(str(p))
                # skalieren
                w, h = img.wrap(0, 0)
                scale = min(max_w / w, max_h / h) if w and h else 1.0
                img._restrictSize(max_w, max_h)
                return img
    except Exception:
        pass
    return None

def build_final_pdf_bytes(tr) -> bytes:
    """
    Erzeugt die finale PDF für den Reisekostenantrag `tr` (TravelRequest),
    inkl. sichtbarer Genehmigungs-Historie (Stempel) und optionaler Unterschriftenbilder.
    """
    buffer = BytesIO()

    # Dokument
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallMuted", fontSize=9, textColor=colors.grey))

    story = []

    # Kopf
    title = f"Reisekostenantrag #{tr.pk}"
    story.append(Paragraph(_safe_text(title), styles["Title"]))
    sub = f"Antragsteller: {tr.applicant.get_full_name() or tr.applicant.username} – {tr.applicant.email}"
    story.append(Paragraph(_safe_text(sub), styles["Normal"]))
    story.append(Paragraph(f"Erstellt am: {timezone.localtime(tr.created_at).strftime('%d.%m.%Y %H:%M')}", styles["SmallMuted"]))
    story.append(Spacer(1, 6*mm))

    # Sequenz (sichtbar)
    story.append(Paragraph("Genehmigungsreihenfolge", styles["Heading3"]))
    seq = tr.approval_sequence()
    seq_rows = [["#","Funktion"]]
    for i, fn in enumerate(seq, start=1):
        seq_rows.append([str(i), _safe_text(fn.name)])
    t = Table(seq_rows, colWidths=[12*mm, 140*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), colors.lightgrey),
        ("TEXTCOLOR",(0,0),(-1,0), colors.black),
        ("GRID",(0,0),(-1,-1), 0.5, colors.grey),
        ("ALIGN",(0,0),(0,-1), "CENTER"),
        ("VALIGN",(0,0),(-1,-1), "MIDDLE"),
        ("FONTSIZE",(0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,0), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 5*mm))

    # Historie/Stempel
    story.append(Paragraph("Entscheidungshistorie (Stempel)", styles["Heading3"]))
    ev_rows = [["Step","Funktion","Entscheider","Entscheidung","Zeit/Ort","Kommentar","Signatur"]]
    for ev in tr.events.all().order_by("created_at"):
        when = timezone.localtime(ev.created_at).strftime("%d.%m.%Y %H:%M")
        who = ev.actor.get_full_name() or ev.actor.username
        ip = ev.ip_address or "–"
        cmt = ev.comment or ""
        sig_img = _sig_image_or_none(ev.actor)

        # Signature als Flowable oder Platzhalter
        sig_cell = sig_img if sig_img else Paragraph("—", styles["SmallMuted"])

        ev_rows.append([
            str(ev.step_number),
            _safe_text(ev.function.name),
            _safe_text(who),
            _safe_text(ev.get_decision_display()),
            _safe_text(f"{when} (IP: {ip})"),
            _safe_text(cmt),
            sig_cell,
        ])

    ev_table = Table(ev_rows, colWidths=[12*mm, 32*mm, 35*mm, 28*mm, 40*mm, 35*mm, 25*mm])
    ev_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), colors.lightgrey),
        ("GRID",(0,0),(-1,-1), 0.5, colors.grey),
        ("VALIGN",(0,0),(-1,-1), "TOP"),
        ("FONTSIZE",(0,0),(-1,-1), 9),
        ("ALIGN",(0,0),(0,-1), "CENTER"),
    ]))
    story.append(ev_table)
    story.append(Spacer(1, 6*mm))

    # Footer-Hinweis
    story.append(Paragraph(
        "Hinweis: Dieses Dokument wurde nach Abschluss aller Genehmigungsschritte automatisch erzeugt.",
        styles["SmallMuted"]
    ))

    # optional: Unterschrift Antragsteller am Ende
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Unterschrift Antragsteller (falls hinterlegt):", styles["SmallMuted"]))
    app_sig = _sig_image_or_none(tr.applicant)
    if app_sig:
        story.append(app_sig)
    else:
        story.append(Paragraph("—", styles["SmallMuted"]))

    doc.build(story)
    return buffer.getvalue()
